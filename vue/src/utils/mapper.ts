import { format } from 'date-fns';
import { formatInTimeZone } from 'date-fns-tz';

import { getQString } from './query';

function formatDate(date: Date, f: string, useLocalTime?: boolean): string {
  if (useLocalTime) return formatInTimeZone(date, tz.value, f);
  return format(date, f);
}

function mapSession(session: HipeacSession, useLocalTime?: boolean): HipeacSession {
  return {
    ...session,
    has_ended: new Date(session.end_at) < new Date(),
    start: new Date(session.start_at),
    end: new Date(session.end_at),
    start_day: formatDate(new Date(session.start_at), 'PP', useLocalTime),
    start_time: formatDate(new Date(session.start_at), 'HH:mm', useLocalTime),
    end_time: formatDate(new Date(session.end_at), 'HH:mm', useLocalTime),
    _q: getQString(session, ['title']),
    color:
      {
        Course: 'teal',
        Keynote: 'primary',
        'Paper Track': 'light-blue',
        'Poster Session': 'cyan',
        'Industrial Session': 'deep-purple',
        Workshop: 'green',
        Tutorial: 'teal',
        'Social Event': 'yellow',
      }[session.type.value] || 'grey-7',
  };
}

export { mapSession };
