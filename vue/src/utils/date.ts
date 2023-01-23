import { intervalToDuration, format as dateFormat, parseISO } from 'date-fns';

const dateFromISO = (date: string): Date => {
  return parseISO(date);
};

const format = (date: Date | number | string, formatStr = 'PP'): string => {
  if (typeof date === 'string') {
    date = dateFromISO(date);
  }

  return dateFormat(date, formatStr);
};

export { dateFromISO, intervalToDuration, format };
