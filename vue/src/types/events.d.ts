interface HipeacImages {
  th: string;
  md: string;
  lg: string;
}

interface HipeacSession extends ApiObject {
  rel_attendees: ApiEndpoint;
  title: string;
  summary: string;
  start_at: string;
  end_at: string;
  type: {
    id: number;
    value: string;
  };
  program: string | null;
  main_speaker: object | null;
  // -----
  _q?: string;
  _registered?: boolean;
  has_ended?: boolean;
  start?: Date;
  end?: Date;
  start_day?: string;
  start_time?: string;
  end_day?: string;
  end_time?: string;
  color?: string;
}

interface HipeacEvent {
  id: number;
  self: string;
  url: string;
  name: string;
  dates: string[];
  type: string;
  is_finished: boolean;
  is_ready: boolean;
  is_virtual: boolean;
  city: string;
  country: Country;
  slug: string;
  hashtag: string;
  start_date: string;
  end_date: string;
  payments_activation: string;
  registration_start_date: string;
  registration_early_deadline: string;
  registration_deadline: string;
  registrations_count: number;
  images: HipeacImages | null;
}

interface HipeacEventAttendee {
  created_at: string;
  user: User;
}
