interface Country {
  name: string;
  code: string;
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
