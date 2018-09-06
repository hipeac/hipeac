from django.core.exceptions import ValidationError


BADWORDS = [
    'anal',
    'anus',
    'ballsack',
    'blowjob',
    'blow job',
    'boner',
    'clitoris',
    'cock',
    'cunt',
    'dick',
    'dildo',
    'dyke',
    'fag',
    'fuck',
    'guns',
    'jizz',
    'labia',
    'muff',
    'nigger',
    'nigga',
    'penis',
    'piss',
    'pussy',
    'scrotum',
    'sex',
    'shit',
    'slut',
    'smegma',
    'spunk',
    'terrorist',
    'terrorists',
    'twat',
    'vagina',
    'wank',
    'whore',
]


def validate_no_badwords(text):
    words = text.lower().split(' ')
    for word in BADWORDS:
        if word in words:
            raise ValidationError(f'"{word}" is not a valid word')
