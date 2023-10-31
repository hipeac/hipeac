import { LocalStorage } from 'quasar';

type StorageItem = {
  value: any;
  ttl: number | null;
};

class Storage {
  readonly ONE_MINUTE: number = 60;
  readonly ONE_HOUR: number = 60 * this.ONE_MINUTE;
  readonly ONE_DAY: number = 24 * this.ONE_HOUR;

  clear() {
    LocalStorage.clear();
  }

  clearExpired() {
    for (const key in LocalStorage.getAllKeys()) {
      this.get(key);
    }
  }

  get(key: string): any | null {
    const item: StorageItem | null = LocalStorage.getItem(key);

    if (!item) {
      return null;
    }

    if (item.ttl && item.ttl < Date.now()) {
      this.remove(key);
      return null;
    }

    return item.value;
  }

  remove(key: string | string[]): void {
    if (Array.isArray(key)) {
      for (const i in key) {
        LocalStorage.remove(key[i]);
      }
    } else {
      LocalStorage.remove(key);
    }
  }

  set(key: string, value: any, ttl: number | null = null): void {
    LocalStorage.set(key, {
      value: value,
      ttl: ttl === null ? null : Date.now() + ttl * 1000,
    });
  }
}

export const storage = new Storage();
