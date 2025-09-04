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

  // Auth
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

  // Startups
  getStartups(skip?: number, limit?: number, options?: RequestOptions): Observable<StartupList[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<StartupList[]>(`/startups${qs}`, options);
  }

  getStartup(startupId: number, options?: RequestOptions): Observable<StartupDetail> {
    return this.http.get<StartupDetail>(`/startups/${encodeURIComponent(String(startupId))}`, options);
  }

  getFounderImage(startupId: number, founderId: number, _options?: RequestOptions): Observable<Blob> {
    const base = this.http.getBaseUrl().replace(/\/+$/, '');
    const url = `${base}/startups/${encodeURIComponent(String(startupId))}/founders/${encodeURIComponent(String(founderId))}/image`;
    const auth = this.http.getAuthHeaderPair();

    return new Observable<Blob>((subscriber) => {
      const headers: Record<string, string> = {Accept: 'image/*'};
      if (auth) headers[auth.name] = auth.value;

      fetch(url, {
        method: 'GET',
        headers,
        cache: 'no-store',
        mode: 'cors'
      })
        .then(async (res) => {
          if (!res.ok) {
            const text = await res.text().catch(() => '');
            throw new Error(`Image fetch failed (${res.status}) ${text?.slice(0, 200)}`);
          }
          return res.blob();
        })
        .then((blob) => {
          subscriber.next(blob);
          subscriber.complete();
        })
        .catch((err) => {
          subscriber.error(err);
        });
    });
  }

  // Investors
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

  // Partners
  getPartners(skip?: number, limit?: number, options?: RequestOptions): Observable<Partner[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<Partner[]>(`/partners${qs}`, options);
  }

  getPartner(partnerId: number, options?: RequestOptions): Observable<Partner> {
    return this.http.get<Partner>(`/partners/${encodeURIComponent(String(partnerId))}`, options);
  }

  // News
  getNews(skip?: number, limit?: number, options?: RequestOptions): Observable<News[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<News[]>(`/news${qs}`, options);
  }

  getNewsItem(newsId: number, options?: RequestOptions): Observable<NewsDetail> {
    return this.http.get<NewsDetail>(`/news/${encodeURIComponent(String(newsId))}`, options);
  }

  getNewsImage(newsId: number, options?: RequestOptions): Observable<{ image_url: string }> {
    return this.http.get<{ image_url: string }>(
      `/news/${encodeURIComponent(String(newsId))}/image`,
      options
    );
  }

  // Events
  getEvents(skip?: number, limit?: number, options?: RequestOptions): Observable<Event[]> {
    const qs = this.buildQuery({skip, limit});
    return this.http.get<Event[]>(`/events${qs}`, options);
  }

  getEvent(eventId: number, options?: RequestOptions): Observable<Event> {
    return this.http.get<Event>(`/events/${encodeURIComponent(String(eventId))}`, options);
  }

  getEventImage(eventId: number, options?: RequestOptions): Observable<{ image_url: string }> {
    return this.http.get<{ image_url: string }>(
      `/events/${encodeURIComponent(String(eventId))}/image`,
      options
    );
  }

  // Users
  getUsers(options?: RequestOptions): Observable<User[]> {
    return this.http.get<User[]>(`/users`, options);
  }

  getUser(userId: number, options?: RequestOptions): Observable<User> {
    return this.http.get<User>(`/users/${encodeURIComponent(String(userId))}`, options);
  }

  getUserByEmail(email: string, options?: RequestOptions): Observable<User> {
    return this.http.get<User>(`/users/email/${encodeURIComponent(email)}`, options);
  }

  getUserImage(userId: number, options?: RequestOptions): Observable<any> {
    return this.http.get<any>(`/users/${encodeURIComponent(String(userId))}/image`, options);
  }
}