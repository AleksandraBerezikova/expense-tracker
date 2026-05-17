import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '2m',  target: 50 },
    { duration: '30s', target: 0  },
  ],
};

const BASE = 'http://51.250.92.75:30080';

export default function () {
  const r1 = http.get(`${BASE}/health`);
  check(r1, { 'health ok': (r) => r.status === 200 });

  const r2 = http.get(`${BASE}/expenses`);
  check(r2, { 'list ok': (r) => r.status === 200 });

  sleep(0.2);
}
