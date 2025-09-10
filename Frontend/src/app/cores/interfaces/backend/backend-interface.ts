import {Observable} from "rxjs";
import {Injectable} from "@angular/core";
import {HttpInterface, RequestOptions} from "../http/http-interface";
import {Event, Investor, News, NewsDetail, Partner, StartupDetail, StartupList, User} from "./dtos";

@Injectable({providedIn: 'root'})
export class BackendInterface {

  constructor(private http: HttpInterface) {
  }

  private buildQuery(params: Record<string, unknown>): string {
    const query = Object.entries(params)
      .filter(([_, v]) => v !== undefined && v !== null)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join("&");
    return query ? `?${query}` : "";
  }

  requestRegister(email: string): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(
      `/auth/request-register`,
      {email},
      {absolutePath: true}
    );
  }

  verifyRegisterCode(payload: { email: string; code: string }): Observable<{
    pre_fill?: { name?: string | null; role?: string | null } | null;
    detail: string
  }> {
    return this.http.post<{ pre_fill?: { name?: string | null; role?: string | null } | null; detail: string }>(
      `/auth/verify-register-code`,
      payload,
      {absolutePath: true}
    );
  }

  completeRegister(payload: {
    email: string;
    code: string;
    name?: string;
    password?: string;
    role?: string
  }): Observable<{
    access_token: string | null;
    token_type: string | null;
    user: User | null;
    detail?: string | null
  }> {
    return this.http.post<{
      access_token: string | null;
      token_type: string | null;
      user: User | null;
      detail?: string | null
    }>(
      `/auth/complete-register`,
      payload,
      {absolutePath: true}
    );
  }

  register(payload: { email: string; name: string; password: string; role?: string }): Observable<unknown> {
    return this.http.post<unknown>(
      `/auth/register`,
      payload,
      {absolutePath: true}
    );
  }

  login(payload: { email: string; password: string }): Observable<unknown> {
    return this.http.post<unknown>(
      `/auth/login`,
      payload,
      {absolutePath: true}
    );
  }

  me(): Observable<User> {
    return this.http.get<User>(
      `/auth/me`,
      {absolutePath: true}
    );
  }

  getStartups(skip?: number, limit?: number, options?: RequestOptions): Observable<StartupList[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<StartupList[]>(`/startups${qs}`, options);
  }

  getStartup(startupId: number, options?: RequestOptions): Observable<StartupDetail> {
    return this.http.get<StartupDetail>(`/startups/${encodeURIComponent(String(startupId))}`, options);
  }

  getFounderImage(founderId: number, options?: RequestOptions): Observable<{ image_url: string }> {
    return this.http.get<{ image_url: string }>(`/founders/${encodeURIComponent(String(founderId))}/image`, options);
  }

  getInvestors(skip?: number, limit?: number, options?: RequestOptions): Observable<Investor[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<Investor[]>(`/investors${qs}`, options);
  }

  getInvestor(investorId: number, options?: RequestOptions): Observable<Investor> {
    return this.http.get<Investor>(`/investors/${encodeURIComponent(String(investorId))}`, options);
  }

  getInvestorImage(investorId: number, options?: RequestOptions): Observable<{ image_url: string }> {
    return this.http.get<{ image_url: string }>(
      `/investors/${encodeURIComponent(String(investorId))}/image`,
      options
    );
  }

  getPartners(skip?: number, limit?: number, options?: RequestOptions): Observable<Partner[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<Partner[]>(`/partners${qs}`, options);
  }

  getPartner(partnerId: number, options?: RequestOptions): Observable<Partner> {
    return this.http.get<Partner>(`/partners/${encodeURIComponent(String(partnerId))}`, options);
  }

  getNews(skip?: number, limit?: number, options?: RequestOptions): Observable<News[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<News[]>(`/news/${qs}`, options);
  }

  getNewsItem(newsId: number, options?: RequestOptions): Observable<NewsDetail> {
    return this.http.get<NewsDetail>(`/news/${encodeURIComponent(String(newsId))}`, options);
  }

  getNewsImage(newsId: number, options?: RequestOptions): Observable<{ image_url: string }> {
    return this.http.get<{ image_url: string }>(
      `/news/${encodeURIComponent(String(newsId))}/image/`,
      options
    );
  }

  getEvents(skip?: number, limit?: number, options?: RequestOptions): Observable<Event[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<Event[]>(`/events/${qs}`, options);
  }

  getEvent(eventId: number, options?: RequestOptions): Observable<Event> {
    return this.http.get<Event>(`/events/${encodeURIComponent(String(eventId))}`, options);
  }

  getEventImage(eventId: number, options?: RequestOptions): Observable<{ image_url: string }> {
    return this.http.get<{ image_url: string }>(
      `/events/${encodeURIComponent(String(eventId))}/image/`,
      options
    );
  }

  getUsers(options?: RequestOptions): Observable<User[]> {
    return this.http.get<User[]>(`/users/`, options);
  }

  getUser(userId: number, options?: RequestOptions): Observable<User> {
    return this.http.get<User>(`/users/${encodeURIComponent(String(userId))}`, options);
  }

  getUserByEmail(email: string, options?: RequestOptions): Observable<User> {
    return this.http.get<User>(`/users/email/${encodeURIComponent(email)}`, options);
  }

  getUserImage(userId: number, options?: RequestOptions): Observable<any> {
    return this.http.get<any>(`/users/${encodeURIComponent(String(userId))}/image/`, options);
  }

  createStartup(payload: {
    name: string;
    email: string;
    legal_status?: string | null;
    address?: string | null;
    phone?: string | null;
    sector?: string | null;
    maturity?: string | null;
    description?: string | null;
    website_url?: string | null;
    social_media_url?: string | null;
    project_status?: string | null;
    needs?: string | null;
  }, options?: RequestOptions): Observable<StartupList> {
    return this.http.post<StartupList>(`/startups/`, payload, options);
  }

  updateStartup(startupId: number, payload: {
    name?: string | null;
    legal_status?: string | null;
    address?: string | null;
    email?: string | null;
    phone?: string | null;
    sector?: string | null;
    maturity?: string | null;
    description?: string | null;
    website_url?: string | null;
    social_media_url?: string | null;
    project_status?: string | null;
    needs?: string | null;
  }, options?: RequestOptions): Observable<StartupList> {
    return this.http.put<StartupList>(`/startups/${encodeURIComponent(String(startupId))}`, payload, options);
  }

  deleteStartup(startupId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.delete<unknown>(`/startups/${encodeURIComponent(String(startupId))}`, options);
  }

  incrementStartupView(startupId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.post<unknown>(`/startups/${encodeURIComponent(String(startupId))}/view/`, options);
  }

  getStartupView(startupId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.get<unknown>(`/startups/${encodeURIComponent(String(startupId))}/view/`, options);
  }

  createInvestor(payload: {
    name: string;
    email: string;
    legal_status?: string | null;
    address?: string | null;
    phone?: string | null;
    investor_type?: string | null;
    investment_focus?: string | null;
    description?: string | null;
  }, options?: RequestOptions): Observable<Investor> {
    return this.http.post<Investor>(`/investors`, payload, options);
  }

  updateInvestor(investorId: number, payload: {
    name?: string | null;
    legal_status?: string | null;
    address?: string | null;
    email?: string | null;
    phone?: string | null;
    investor_type?: string | null;
    investment_focus?: string | null;
    description?: string | null;
  }, options?: RequestOptions): Observable<Investor> {
    return this.http.put<Investor>(`/investors/${encodeURIComponent(String(investorId))}`, payload, options);
  }

  deleteInvestor(investorId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.delete<unknown>(`/investors/${encodeURIComponent(String(investorId))}`, options);
  }

  createPartner(payload: {
    name: string;
    email: string;
    legal_status?: string | null;
    address?: string | null;
    phone?: string | null;
    partnership_type?: string | null;
    description?: string | null;
  }, options?: RequestOptions): Observable<Partner> {
    return this.http.post<Partner>(`/partners`, payload, options);
  }

  updatePartner(partnerId: number, payload: {
    name?: string | null;
    legal_status?: string | null;
    address?: string | null;
    email?: string | null;
    phone?: string | null;
    partnership_type?: string | null;
    description?: string | null;
  }, options?: RequestOptions): Observable<Partner> {
    return this.http.put<Partner>(`/partners/${encodeURIComponent(String(partnerId))}`, payload, options);
  }

  deletePartner(partnerId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.delete<unknown>(`/partners/${encodeURIComponent(String(partnerId))}`, options);
  }

  createNews(payload: {
    title: string;
    news_date?: string | null;
    location?: string | null;
    category?: string | null;
    startup_id?: number | null;
    description?: string | null;
  }, options?: RequestOptions): Observable<News> {
    return this.http.post<News>(`/news`, payload, options);
  }

  updateNews(newsId: number, payload: {
    title?: string | null;
    news_date?: string | null;
    location?: string | null;
    category?: string | null;
    startup_id?: number | null;
    description?: string | null;
  }, options?: RequestOptions): Observable<News> {
    return this.http.put<News>(`/news/${encodeURIComponent(String(newsId))}`, payload, options);
  }

  deleteNews(newsId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.delete<unknown>(`/news/${encodeURIComponent(String(newsId))}`, options);
  }

  createEvent(payload: {
    name: string;
    dates: string;
    location: string;
    description: string;
    event_type: string;
    target_audience: string;
  }, options?: RequestOptions): Observable<Event> {
    return this.http.post<Event>(`/events`, payload, options);
  }

  updateEvent(eventId: number, payload: {
    name?: string | null;
    dates?: string | null;
    location?: string | null;
    description?: string | null;
    event_type?: string | null;
    target_audience?: string | null;
  }, options?: RequestOptions): Observable<Event> {
    return this.http.put<Event>(`/events/${encodeURIComponent(String(eventId))}`, payload, options);
  }

  deleteEvent(eventId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.delete<unknown>(`/events/${encodeURIComponent(String(eventId))}`, options);
  }

  createUser(payload: {
    email: string;
    name: string;
    password: string;
    role?: string;
    founder_id?: number | null;
    investor_id?: number | null;
  }, options?: RequestOptions): Observable<User> {
    return this.http.post<User>(`/users`, payload, options);
  }

  updateUser(userId: number, payload: {
    email?: string | null;
    name?: string | null;
    role?: string | null;
    founder_id?: number | null;
    investor_id?: number | null;
  }, options?: RequestOptions): Observable<User> {
    return this.http.put<User>(`/users/${encodeURIComponent(String(userId))}`, payload, options);
  }

  deleteUser(userId: number, options?: RequestOptions): Observable<unknown> {
    return this.http.delete<unknown>(`/users/${encodeURIComponent(String(userId))}`, options);
  }

  adminSync(options?: RequestOptions): Observable<unknown> {
    return this.http.post<unknown>(`/admin/sync`, {}, options);
  }
}