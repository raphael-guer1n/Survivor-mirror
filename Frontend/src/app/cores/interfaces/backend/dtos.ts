export interface Event {
    id: number;
    name: string;
    dates?: string | null;
    location?: string | null;
    description?: string | null;
    event_type?: string | null;
    target_audience?: string | null;
}

export interface Founder {
    id: number;
    name: string;
    startup_id: number;
}

export interface Investor {
    id: number;
    name: string;
    email: string;
    legal_status?: string | null;
    address?: string | null;
    phone?: string | null;
    created_at?: string | null;
    description?: string | null;
    investor_type?: string | null;
    investment_focus?: string | null;
}

export interface News {
    id: number;
    title: string;
    news_date?: string | null;
    location?: string | null;
    category?: string | null;
    startup_id?: number | null;
}

export interface NewsDetail extends News {
    description: string;
}

export interface Partner {
    id: number;
    name: string;
    email: string;
    legal_status?: string | null;
    address?: string | null;
    phone?: string | null;
    created_at?: string | null;
    description?: string | null;
    partnership_type?: string | null;
}

export interface StartupDetail {
    id: number;
    name: string;
    email: string;
    legal_status?: string | null;
    address?: string | null;
    phone?: string | null;
    created_at?: string | null;
    description?: string | null;
    website_url?: string | null;
    social_media_url?: string | null;
    project_status?: string | null;
    needs?: string | null;
    sector?: string | null;
    maturity?: string | null;
    founders?: Founder[];         // default [] on backend, optional in DTO
}

export interface StartupList {
    id: number;
    name: string;
    email: string;
    legal_status?: string | null;
    address?: string | null;
    phone?: string | null;
    sector?: string | null;
    maturity?: string | null;
}

export interface User {
    id: number;
    email: string;
    name: string;
    role: string;
    founder_id?: number | null;
    investor_id?: number | null;
}

export interface ValidationError {
    loc: Array<string | number>;
    msg: string;
    type: string;
}

export interface HTTPValidationError {
    detail?: ValidationError[];
}

export type StartupListResponse = StartupList[];
export type InvestorListResponse = Investor[];
export type PartnerListResponse = Partner[];
export type NewsListResponse = News[];
export type EventListResponse = Event[];
export type UsersListResponse = User[];