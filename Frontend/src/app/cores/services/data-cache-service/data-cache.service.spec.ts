import { TestBed } from '@angular/core/testing';

import { DataCacheService } from './data-cache.service';

describe('DataCache', () => {
  let service: DataCacheService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DataCacheService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
