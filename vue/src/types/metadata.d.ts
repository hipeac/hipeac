interface Country {
  name: string;
  code: string;
}

interface Link {
  id: number;
  url: Url;
  type: 'website' | 'twitter' | 'linkedin' | 'youtube' | 'other';
  type_display: string;
}

interface Metadata {
  id: number;
  type: string;
  value: string;
  position: number;
  keywords: string[];
  // -----
  count?: number;
}

interface ApplicationArea extends Metadata {
  type: 'application_area';
}

interface CareerLevel extends Metadata {
  type: 'job_position';
}

interface EmploymentType extends Metadata {
  type: 'employment_type';
}

interface Topic extends Metadata {
  type: 'topic';
}

interface HipeacImages {
  th: string;
  md: string;
  lg: string;
}

interface QuasarOption {
  value: number | string | null;
  label: string;
}
