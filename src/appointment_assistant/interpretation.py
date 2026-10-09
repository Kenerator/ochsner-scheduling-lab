"""Validated proposals only. Consent and service identifiers never enter this boundary."""
import re
from .models import ProposedAction, SPECIALTIES, LOCATIONS, ValidationError, valid_date, valid_phone, valid_zip

INTENTS = ('provider_lookup','book','appointment_lookup','human_request','medical_advice','unsupported','decline','reset','unclear')
FIELD_NAMES = ('phone','dob','zip_code','start_date','end_date','specialty','location')

class InterpretationError(ValueError):
    """Safe extraction failure; caller must never silently fall back to simulation."""

# Exact native contract, embedded so an installed package does not need specs/.
INTERPRETATION_SCHEMA = {
    'type':'object', 'additionalProperties':False,
    'required':['intent','fields','option_ordinal'],
    'properties': {
        'intent': {'type':'string','enum':list(INTENTS)},
        'fields': {'type':'object','additionalProperties':False,
                   'properties':{name: {'type':['string','null']} for name in FIELD_NAMES},
                   'required':list(FIELD_NAMES)},
        'option_ordinal': {'type':['integer','null']},
    },
}
INTERPRETATION_SCHEMA['properties']['fields']['properties']['specialty']['enum'] = [*SPECIALTIES,None]
INTERPRETATION_SCHEMA['properties']['fields']['properties']['location']['enum'] = [*LOCATIONS,None]

def validate_action(payload):
    try:
        if not isinstance(payload, dict) or set(payload) != {'intent','fields','option_ordinal'}:
            raise ValueError()
        if payload['intent'] not in INTENTS: raise ValueError()
        fields = payload['fields']
        if not isinstance(fields, dict) or set(fields) != set(FIELD_NAMES): raise ValueError()
        for key, value in fields.items():
            if value is None: continue
            if not isinstance(value, str) or len(value) > 64: raise ValueError()
            if key in ('dob','start_date','end_date'): valid_date(value)
            elif key == 'phone': valid_phone(value)
            elif key == 'zip_code': valid_zip(value)
            elif key == 'specialty' and value not in SPECIALTIES: raise ValueError()
            elif key == 'location' and value not in LOCATIONS: raise ValueError()
        if fields['start_date'] and fields['end_date'] and fields['start_date'] > fields['end_date']: raise ValueError()
        ordinal = payload['option_ordinal']
        if ordinal is not None and (type(ordinal) is not int or not 1 <= ordinal <= 100): raise ValueError()
        return ProposedAction(payload['intent'], fields.copy(), ordinal)
    except (ValueError, TypeError, KeyError, ValidationError):
        raise InterpretationError('Invalid interpretation') from None

class RehearsalInterpreter:
    """Explicit deterministic rehearsal; does not demonstrate live AI capability."""
    def interpret(self, text, context):
        if not isinstance(text,str) or len(text)>8000: raise InterpretationError('Invalid input')
        low=text.strip().casefold(); fields=dict.fromkeys(FIELD_NAMES)
        if low in ('yes','confirm'): return ProposedAction('unclear',fields,None)
        intent=context.get('intent','unclear')
        if intent not in INTENTS: intent='unclear'
        if re.search(r'\b(human|person|representative|agent)\b',low): intent='human_request'
        elif re.search(r'\b(medicine|symptom|diagnos\w*|medical advice|chest pain|treatment)\b',low): intent='medical_advice'
        elif re.search(r'\b(cancel|reschedule|surgery)\b',low): intent='unsupported'
        elif low in ('reset','start over'): intent='reset'
        elif low in ('no','decline','never mind'): intent='decline'
        elif re.search(r'\b(my appointments|existing appointments|appointment lookup)\b',low): intent='appointment_lookup'
        elif re.search(r'\b(book|schedule|booking)\b',low): intent='book'
        elif re.search(r'\b(provider|providers|doctors|doctor)\b',low): intent='provider_lookup'
        for specialty in SPECIALTIES:
            if specialty.replace('_',' ') in low or specialty in low: fields['specialty']=specialty
        for location in LOCATIONS:
            if re.search(r'\b'+location+r'\b',low): fields['location']=location
        dates=re.findall(r'\b\d{4}-\d{2}-\d{2}\b',low)
        dob_match=re.search(r'(?:dob|born|birth(?:day| date)?|date of birth)\s*[:=]?\s*(\d{4}-\d{2}-\d{2})',low)
        if dob_match: fields['dob']=dob_match.group(1); dates.remove(dob_match.group(1))
        elif len(dates)==1 and not fields['specialty'] and not any(w in low for w in ('from','after','before','start','end','between')): fields['dob']=dates.pop()
        if dates: fields['start_date']=dates[0]
        if len(dates)>1: fields['end_date']=dates[1]
        phone=re.search(r'(?<!\d)(?:\+?1[- .]?)?(?:\(?\d{3}\)?[- .]?)?\d{3}[- .]\d{4}(?!\d)',low)
        if phone: fields['phone']=phone.group()
        zip_match=re.search(r'(?:zip(?: code)?\s*[:=]?\s*)?\b(\d{5})\b',low)
        if zip_match: fields['zip_code']=zip_match.group(1)
        ordinal=None
        for word,number in (('first',1),('second',2),('third',3),('fourth',4)):
            if re.search(r'\b'+word+r'\b',low): ordinal=number
        number=re.fullmatch(r'(?:option\s*)?(\d{1,2})',low)
        if number: ordinal=int(number.group(1))
        # Current-choice bounds belong to Session so invalid choices retain context.
        return validate_action(dict(intent=intent, fields=fields, option_ordinal=ordinal))
