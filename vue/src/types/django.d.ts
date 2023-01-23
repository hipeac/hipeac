interface DjangoPermission {
  id: number;
  name: string;
  content_type: number;
  codename: string;
}

interface DjangoGroup {
  id: number;
  name: string;
  permissions: DjangoPermission[];
}

interface DjangoAuthenticatedUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_active: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string;
  groups: DjangoGroup[];
  permissions: DjangoPermission[];
}
