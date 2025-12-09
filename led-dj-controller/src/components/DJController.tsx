import { useState, useEffect } from 'react';
import type { LED } from '../api/ledApi';
import { ledApi } from '../api/ledApi';
import LEDButton from './LEDButton';
import './DJController.css';

const DJController = () => {
  const [leds, setLeds] = useState<LED[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Загрузка светодиодов при монтировании компонента
  useEffect(() => {
    loadLeds();
  }, []);

  const loadLeds = async () => {
    try {
      setLoading(true);
      const data = await ledApi.getAllLeds();
      setLeds(data);
      setError(null);
    } catch (err) {
      setError('Не удалось подключиться к API. Убедитесь, что сервер запущен на порту 5001');
      console.error('Error loading LEDs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (led: LED) => {
    try {
      const newState = led.состояние === 'вкл' ? 'выкл' : 'вкл';
      const updatedLed = await ledApi.updateLed(led.id, newState);
      
      // Обновляем состояние в UI
      setLeds(leds.map(l => l.id === updatedLed.id ? updatedLed : l));
    } catch (err) {
      console.error('Error toggling LED:', err);
      setError('Ошибка переключения светодиода');
    }
  };

  if (loading) {
    return (
      <div className="dj-controller">
        <div className="loading">
          <div className="spinner"></div>
          <p>Загрузка...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dj-controller">
        <div className="error">
          <h2>⚠️ Ошибка</h2>
          <p>{error}</p>
          <button onClick={loadLeds} className="retry-button">
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dj-controller">
      <header className="header">
        <h1>🎛️ LED DJ Controller</h1>
        <p className="subtitle">Управление 12 светодиодами Arduino</p>
      </header>

      <div className="led-grid">
        {leds.map((led) => (
          <LEDButton
            key={led.id}
            led={led}
            onToggle={() => handleToggle(led)}
          />
        ))}
      </div>

      <footer className="footer">
        <div className="status">
          <span className="status-indicator active"></span>
          <span>Подключено к Arduino</span>
        </div>
      </footer>
    </div>
  );
};

export default DJController;
