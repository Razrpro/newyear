export interface LED {
  id: number;
  название: string;
  pin: number;
  состояние: string;
}

// Используем относительный путь - Vite проксирует /api на http://localhost:5001
const API_BASE_URL = '/api';

export const ledApi = {
  // Получить все светодиоды
  getAllLeds: async (): Promise<LED[]> => {
    const response = await fetch(`${API_BASE_URL}/leds/`);
    if (!response.ok) {
      throw new Error('Failed to fetch LEDs');
    }
    return response.json();
  },

  // Обновить состояние светодиода
  updateLed: async (id: number, состояние: string): Promise<LED> => {
    const response = await fetch(`${API_BASE_URL}/leds/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ состояние }),
    });
    if (!response.ok) {
      throw new Error('Failed to update LED');
    }
    return response.json();
  },

  // Включить светодиод
  turnOn: async (id: number): Promise<LED> => {
    const response = await fetch(`${API_BASE_URL}/leds/${id}/on`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to turn on LED');
    }
    return response.json();
  },

  // Выключить светодиод
  turnOff: async (id: number): Promise<LED> => {
    const response = await fetch(`${API_BASE_URL}/leds/${id}/off`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to turn off LED');
    }
    return response.json();
  },
};
