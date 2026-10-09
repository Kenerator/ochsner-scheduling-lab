"""Deterministic authority boundary for model-proposed scheduling actions."""
from dataclasses import dataclass
from threading import RLock
import re
from time import monotonic
from .models import ProposedAction
from .interpretation import validate_action
from .scheduling import SchedulingError
from .events import Evidence
from .policy import PolicyGate
from .submission import SubmissionGate

@dataclass(frozen=True)
class TurnResult:
    message: str
    state: str
    outcome: str = 'not_attempted'

class PolicyDenied(Exception):
    pass

class Session:
    """Private in-memory state; repr/export never includes identity or transcripts."""
    def __init__(self,api,interpreter,events=None,policy=None):
        self.api=api;self.interpreter=interpreter
        self.events=events if events is not None else Evidence()
        self.policy=policy if policy is not None else PolicyGate()
        self.gate=SubmissionGate();self._lock=RLock();self._generation=0
        self.fields={};self.intent=None;self.patient=None;self.matches=[]
        self.slots=[];self.providers={};self.proposal=None;self.revision=0
        self.last_booking=None;self.unknown=False;self.unknown_handoff=False;self.identity_failures=0
        self.state='start'

    def submit(self,text,generation=None):
        if generation is None:
            with self._lock:self._generation+=1;generation=self._generation
        return self.gate.execute(generation,lambda:self._turn(text))

    def _result(self,message,state,outcome='not_attempted'):
        self.state=state
        self.events.emit('workflow',state=state,outcome=outcome)
        self.events.emit('latency',elapsed_ms=round((monotonic()-self._turn_started)*1000,3))
        return TurnResult(message,state,outcome)

    def _guard(self,operation,**facts):
        decision=self.policy.evaluate(operation,**{
              'verified':self.patient is not None,'current_slot':self.proposal is not None,
              'current_consent':False,'unknown':self.unknown,**facts})
        self.events.emit('guard',action=operation,code=decision.code,allowed=decision.allowed)
        if not decision.allowed:raise PolicyDenied()

    def _handoff(self,reason,message):
        self.proposal=None;self.slots=[]
        if self.unknown_handoff:
            return self._result(message+' A prior handoff outcome is unknown; contact scheduling staff directly. I will not repeat it.','handoff','unknown')
        self.events.emit('handoff',reason=reason,outcome='not_attempted')
        try:
            self._guard('handoff')
            receipt=self.api.handoff(reason,'Scheduling assistance required: '+reason.replace('_',' ')+'.',
                 patient_id=self.patient['patientId'] if self.patient else None)
            return self._result(message+' A request was queued in the synthetic mock; no human contact is confirmed.','handoff','unknown' if self.unknown else 'completed')
        except SchedulingError as e:
            if e.unknown:
                self.unknown_handoff=True
                return self._result(message+' The handoff outcome is unknown. Contact scheduling staff directly; no automatic retry will occur.','handoff','unknown')
            return self._result(message+' Unable to queue a handoff. Contact scheduling staff directly.','handoff','rejected')
        except PolicyDenied:
            return self._result(message+' Safety validation is unavailable. Contact scheduling staff directly.','blocked','rejected')

    def _turn(self,text):
        with self._lock:
            self._turn_started=monotonic()
            if not isinstance(text,str) or not text.strip() or len(text)>4000:
                return self._result('Enter a short scheduling request.','clarify')
            try:
                context={'intent':self.intent,'state':self.state,'slot_count':len(self.slots),
                         'fields_present':sorted(self.fields)}
                a=self.interpreter.interpret(text,context)
                if isinstance(a,ProposedAction):
                    a=validate_action({'intent':a.intent,'fields':a.fields,'option_ordinal':a.option_ordinal})
                if not isinstance(a,ProposedAction):
                    return self._result('The AI proposal was invalid. Please rephrase; no scheduling action was taken.','blocked','rejected')
            except Exception:
                return self._result('The AI interpreter is unavailable or returned an invalid proposal. No scheduling action was taken; try again or contact scheduling staff.','blocked','rejected')
            self.events.emit('interpretation',intent=a.intent,action='none',outcome='completed')
            if a.intent=='reset':
                if self.unknown or self.unknown_handoff:
                    return self._result('A previous effect outcome is unknown. Reset cannot establish failure; contact scheduling staff to reconcile it before another booking.','blocked','unknown')
                self.fields={};self.patient=None;self.matches=[];self.slots=[];self.proposal=None
                self.intent=None;self.last_booking=None;self.identity_failures=0;self.revision+=1
                return self._result('Conversation reset. The reference mock bookings remain; restart only your own mock to reset synthetic fixtures.','start')
            meaningful=a.intent in ('provider_lookup','book','appointment_lookup')
            changed_intent=meaningful and a.intent!=self.intent
            patches={k:v for k,v in a.fields.items() if v is not None and self.fields.get(k)!=v}
            identity_changed=bool(set(patches)&{'phone','dob','zip_code'})
            search_changed=bool(set(patches)&{'specialty','location','start_date','end_date'})
            if patches or changed_intent:
                self.revision+=1;self.proposal=None;self.slots=[];self.last_booking=None
                if identity_changed:self.patient=None;self.matches=[]
                self.fields.update(patches)
            if meaningful:self.intent=a.intent
            if a.intent in ('medical_advice','unsupported','human_request'):
                reason={'medical_advice':'medical_advice','unsupported':'unsupported_request','human_request':'user_requested'}[a.intent]
                explanation={'medical_advice':'I cannot provide medical advice or triage. Please speak with a qualified human.',
                    'unsupported':'This request is outside supported scheduling. Please contact scheduling staff.',
                    'human_request':'A human scheduling representative can help.'}[a.intent]
                return self._handoff(reason,explanation)
            if a.intent=='decline' or text.strip().casefold() in ('no','cancel','never mind','nevermind'):
                self.proposal=None;self.slots=[];self.last_booking=None;self.revision+=1
                return self._result('No new booking was made. Tell me a new scheduling request when ready.','clarify')
            try:
                if self.intent=='provider_lookup':
                    if not self.fields.get('specialty'):
                        return self._result('Which specialty: primary care or dermatology?','clarify')
                    if not self.fields.get('location'):
                        return self._result('Which location: downtown, uptown, or lakeside?','clarify')
                    self._guard('providers')
                    providers=self.api.providers(**self._filters(dates=False))
                    if not providers:return self._result('No matching providers were returned. Try another supported location or specialty.','providers')
                    lines=[p['name']+' — '+p['specialty']+' — '+', '.join(p['locations']) for p in providers]
                    return self._result('Providers from the scheduling API:\n'+'\n'.join(lines),'providers')
                if self.intent not in ('book','appointment_lookup'):
                    return self._result('Would you like to find providers, book an appointment, or look up your appointments?','clarify')
                if self.unknown and self.intent=='book':
                    return self._result('A previous booking outcome is unknown. Contact scheduling staff to reconcile it; I will not retry the booking.','blocked','unknown')
                if self.last_booking and not patches and not changed_intent and text.strip().casefold() in ('yes','confirm'):
                    return self._result(self._appointment_text(self.last_booking),'booked','completed')
                if not self.patient:
                    missing=[k for k in ('phone','dob') if not self.fields.get(k)]
                    if missing:
                        label='phone number and date of birth (YYYY-MM-DD)' if len(missing)==2 else ('phone number' if missing[0]=='phone' else 'date of birth (YYYY-MM-DD)')
                        return self._result('Please provide your '+label+' to verify your synthetic patient record.','identity')
                    self._guard('patient_search')
                    self.matches=self.api.search_patients(self.fields['phone'],self.fields['dob'])
                    self.matches=[p for p in self.matches if p['phone']==self.fields['phone'] and p['dateOfBirth']==self.fields['dob']]
                    if len(self.matches)>1:
                        if not self.fields.get('zip_code'):
                            return self._result('I need one more private check. Please provide your ZIP code; I will not show possible patient records.','identity')
                        self.matches=[p for p in self.matches if p['zipCode']==self.fields['zip_code']]
                    if len(self.matches)!=1:
                        self.identity_failures+=1
                        if self.identity_failures>=2 or self.fields.get('zip_code'):
                            return self._handoff('identity_unclear','I could not identify a unique patient. Please contact scheduling staff for identity assistance.')
                        return self._result('No patient match was found. Please check your phone and date of birth, or ask for a human. No patient details are shown.','identity')
                    self.patient=self.matches[0];self.identity_failures=0
                if self.intent=='appointment_lookup':
                    self._guard('appointments')
                    records=self.api.appointments(self.patient['patientId'])
                    return self._result('No appointments were returned.' if not records else '\n'.join(self._appointment_text(x) for x in records),'appointments')
                if not self.fields.get('specialty'):
                    return self._result('Which specialty: primary care or dermatology?','preferences')
                # A new model-proposed choice requires a new summary, even on literal yes.
                if self.proposal and a.option_ordinal is not None:
                    self.proposal=None
                if self.proposal and not patches and not changed_intent:
                    if text.strip().casefold() in ('yes','confirm'):
                        slot=self.proposal['slot'];rev=self.proposal['revision'];patient=self.proposal['patient_id']
                        if rev!=self.revision or patient!=self.patient['patientId'] or slot not in self.slots:
                            self.proposal=None
                            return self._result('The proposal changed. Choose a current option and confirm again.','slots','rejected')
                        self._guard('book',current_slot=True,current_consent=True)
                        self.proposal=None # reserve attempt before dispatch; never reopen after unknown
                        try:
                            appointment=self.api.book(patient,slot)
                        except SchedulingError as e:
                            if e.unknown:
                                self.unknown=True;self.slots=[]
                                return self._handoff('other','The booking outcome is unknown. Do not repeat the booking; scheduling staff must reconcile it.')
                            self.slots=[]
                            if e.status==409:
                                return self._result('That slot is no longer available. Ask to search again, then choose and confirm a fresh option.','conflict','rejected')
                            return self._handoff('api_failure','The booking was rejected by the scheduling system; no booking is confirmed.')
                        self.last_booking=appointment;self.slots=[]
                        return self._result(self._appointment_text(appointment),'booked','completed')
                    if a.option_ordinal is None:
                        return self._result(self.proposal['summary']+' Reply exactly yes or confirm to book, or provide a correction.','proposal')
                if not self.slots:
                    self._guard('availability')
                    self.slots=self.api.availability(self.patient['patientId'],**self._filters())
                    self._guard('providers')
                    returned=self.api.providers(**self._filters(dates=False));self.providers={p['providerId']:p for p in returned}
                    if any(s['providerId'] not in self.providers or
                           s['specialty']!=self.providers[s['providerId']]['specialty'] or
                           s['location'] not in self.providers[s['providerId']]['locations'] for s in self.slots):
                        self.slots=[];return self._handoff('api_failure','The scheduling data could not be validated.')
                    if not self.slots:return self._handoff('no_availability','No available appointments were returned for your preferences.')
                    # A choice cannot refer to options not shown in an earlier turn.
                    return self._result(self._options_text(),'slots')
                if a.option_ordinal is not None:
                    if type(a.option_ordinal) is not int or not 1<=a.option_ordinal<=len(self.slots):
                        self.proposal=None;return self._result('Choose a numbered option currently shown.\n'+self._options_text(),'slots','rejected')
                    slot=self.slots[a.option_ordinal-1]
                    summary='For your verified patient record: '+self._slot_text(slot)+'.'
                    self.proposal={'patient_id':self.patient['patientId'],'slot':slot,'revision':self.revision,'summary':summary}
                    return self._result(summary+' Reply exactly yes or confirm to book. Selection alone does not book.','proposal')
                return self._result(self._options_text()+' Choose a numbered option; I will then ask for confirmation.','slots')
            except PolicyDenied:
                return self._result('The proposed action did not pass safety validation. No scheduling action was taken; contact scheduling staff.','blocked','rejected')
            except SchedulingError as e:
                return self._handoff('api_failure','The scheduling system is unavailable or returned invalid data. No booking is confirmed.')

    def _filters(self,dates=True):
        names=('specialty','location','start_date','end_date') if dates else ('specialty','location')
        return {k:v for k,v in self.fields.items() if k in names}
    def _slot_text(self,slot):
        provider=self.providers[slot['providerId']]['name']
        return provider+' — '+slot['specialty']+' — '+slot['location']+' — '+slot['startTime']
    def _options_text(self):
        return 'Available API options (fixture times use fixed -05:00):\n'+'\n'.join(f'{i}. {self._slot_text(s)}' for i,s in enumerate(self.slots,1))
    def _appointment_text(self,a):
        return 'Appointment '+a['appointmentId']+': '+a['status']+' — '+a['specialty']+' — '+a['location']+' — '+a['startTime']+'.'
