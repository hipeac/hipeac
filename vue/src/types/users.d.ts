interface Profile {
  name: string;
  country: Country | null;
  avatar_url: Url | null;
  institution: Institution | null;
  second_institution: Institution | null;
}

interface User extends ApiObject {
  username: string;
  profile: Profile;
  url: Url;
}
