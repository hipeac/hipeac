interface Institution extends ApiObject {
  type: 'university' | 'lab' | 'innovation' | 'industry' | 'sme' | 'other';
  name: string;
  short_name: string;
  country: Country;
  url: Url;
}
