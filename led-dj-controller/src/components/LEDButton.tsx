import type { LED } from '../api/ledApi';
import './LEDButton.css';

interface LEDButtonProps {
  led: LED;
  onToggle: () => void;
}

const LEDButton = ({ led, onToggle }: LEDButtonProps) => {
  const isOn = led.состояние === 'вкл';

  return (
    <button
      className={`led-button ${isOn ? 'active' : ''}`}
      onClick={onToggle}
      aria-label={`${led.название} - ${isOn ? 'включен' : 'выключен'}`}
    >
      <div className="led-button-inner">
        <div className="led-number">{led.id}</div>
        <div className="led-indicator">
          <div className={`led-light ${isOn ? 'on' : 'off'}`}></div>
        </div>
        <div className="led-label">{led.название}</div>
        <div className="led-pin">Pin {led.pin}</div>
      </div>
    </button>
  );
};

export default LEDButton;
