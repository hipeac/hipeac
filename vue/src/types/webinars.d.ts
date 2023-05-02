interface HipeacWebinar extends HipeacSession {
  rel_register: ApiEndpoint;
  rel_unregister: ApiEndpoint;
  has_ended: boolean;
}

interface HipeacWebinarRegistration {
  id: number;
  uuid: string;
  zoom_access_link: Url;
  user: number;
  webinar: number;
  created_at: string;
  // -----
  Webinar?: HipeacWebinar;
}
