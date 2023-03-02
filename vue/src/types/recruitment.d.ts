interface HipeacJob extends ApiObject {
  title: string;
  url: Url;
  employment_type: 16 | 17; // 16: full-time, 17: internship
  positions: number;
  institution: Institution;
  location: string;
  country: Country;
  deadline: string;
  created_at: string;
  updated_at: string;
  application_areas: ApplicationArea[];
  topics: Topic[];
  career_levels: number[];
  keywords: string[];
  // -----
  EmploymentType?: EmploymentType;
  // -----
  q?: string;
  applicationAreaIds?: Set<number>;
  topicIds?: Set<number>;
  careerLevelIds?: Set<number>;
  tags?: string[];
}

interface JobsFilter {
  typeId: number | null;
  topicIds: number[];
  careerLevelIds: number[];
  countryCodes: string[];
  query: string;
  sort: 'newest' | 'oldest' | 'deadline';
}
