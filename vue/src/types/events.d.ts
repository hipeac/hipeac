interface Country {
  name: string;
  code: string;
}

interface HipeacEventImages {
  th: string;
  md: string;
  lg: string;
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
  images: HipeacEventImage | null;
}
