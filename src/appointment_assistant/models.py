"""Small, closed service-record validators; no eligibility or identity authority."""
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
import re

SPECIALTIES = ('primary_care', 'dermatology')
LOCATIONS = ('downtown', 'uptown', 'lakeside')

@dataclass(frozen=True)
class ProposedAction:
    intent: str
    fields: dict
    option_ordinal: int | None = None

class ValidationError(ValueError):
    """Malformed service data; never include upstream values in the error."""

def valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValidationError('Invalid calendar date')
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValidationError('Invalid calendar date') from None
    return value

def valid_phone(value):
    if not isinstance(value, str) or not 7 <= len(value) <= 32 or not re.fullmatch(r'[+()0-9 .-]+', value) or not 7 <= len(re.sub(r'\D', '', value)) <= 15:
        raise ValidationError('Invalid phone')
    return value

def valid_zip(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{5}', value):
        raise ValidationError('Invalid ZIP')
    return value

def _text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValidationError('Invalid text field')

def _record(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValidationError('Invalid record shape')
    return deepcopy(value)

def _enum(value, allowed):
    if not isinstance(value, str) or value not in allowed:
        raise ValidationError('Invalid enum field')

def _timestamp(value):
    try:
        parsed = datetime.fromisoformat(value) if isinstance(value, str) else None
        if parsed is None or parsed.tzinfo is None or parsed.utcoffset() is None or 'T' not in value:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValidationError('Invalid aware timestamp') from None

def validate_provider(value):
    result = _record(value, ('providerId','name','specialty','locations','modalities'))
    _text(result['providerId']); _text(result['name']); _enum(result['specialty'], SPECIALTIES)
    for key, allowed in (('locations', LOCATIONS), ('modalities', ('in_person','virtual'))):
        if not isinstance(result[key], list) or not result[key]:
            raise ValidationError('Invalid record array')
        for item in result[key]: _enum(item, allowed)
    return result

def validate_patient(value):
    result = _record(value, ('patientId','firstName','lastName','dateOfBirth','phone','zipCode','establishedPatient'))
    for key in ('patientId','firstName','lastName'): _text(result[key])
    valid_date(result['dateOfBirth']); valid_phone(result['phone']); valid_zip(result['zipCode'])
    if type(result['establishedPatient']) is not bool: raise ValidationError('Invalid patient flag')
    return result

def _service_fields(result):
    _text(result['providerId']); _enum(result['specialty'], SPECIALTIES)
    _enum(result['location'], LOCATIONS); _timestamp(result['startTime'])

def validate_slot(value):
    result = _record(value, ('slotId','providerId','specialty','location','startTime','available'))
    _text(result['slotId']); _service_fields(result)
    if result['available'] is not True: raise ValidationError('Unavailable slot')
    return result

def validate_appointment(value):
    result = _record(value, ('appointmentId','patientId','providerId','specialty','location','startTime','status'))
    _text(result['appointmentId']); _text(result['patientId']); _service_fields(result)
    _enum(result['status'], ('scheduled',))
    return result

def validate_handoff(value):
    result = _record(value, ('handoffId','status'))
    _text(result['handoffId']); _enum(result['status'], ('queued',))
    return result
