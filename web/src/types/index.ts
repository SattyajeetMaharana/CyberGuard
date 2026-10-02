export interface User {
  id: string;
  name: string;
  email: string;
  role?: string;
}

export interface Organization {
  id: string;
  name: string;
}

export interface Detection {
  id: string;
  type: string;
  status: string;
  createdAt?: string;
}

export interface Threat {
  id: string;
  category: string;
  riskLevel: string;
  score?: number;
}

export interface Incident {
  id: string;
  title: string;
  status: string;
  createdAt?: string;
}

export interface CyberScore {
  score: number;
  riskLevel?: string;
}

export interface Notification {
  id: string;
  title: string;
  message?: string;
  read: boolean;
  createdAt?: string;
}