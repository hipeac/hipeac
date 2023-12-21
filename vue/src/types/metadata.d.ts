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
}

interface QuasarOption {
  value: number | string;
  label: string;
}
