export interface Category {
  id: number;
  name: string;
  parent_id: number;
}

export interface Product {
  id: number;
  name: string;
  vendor: string;
  description?: string;
  price: number;
  category: number;
  supplier: number;
}

export interface CommonUser {
  email: string;
  firstName: string;
  lastName: string;
  address: string;
  city: string;
  zipcode: string;
}

export interface AuthUser extends CommonUser {
  id: number;
  isStaff: boolean;
  roles: string[];
  token: string;
}

export interface RegisterUser extends CommonUser {
  password: string;
}
