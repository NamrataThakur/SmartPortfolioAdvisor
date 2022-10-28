import React, { useState, useRef } from 'react';
import GAHyperparameters from './GAHyperparameters';
import GAEpoch from './GAEpoch';
import GAResult from './GAResult';

const ConsoleAccordion = ({ message, curState }) => {
  const [active, setActive] = useState(curState);
  const [height, setHeight] = useState('0px');
  const [rotate, setRotate] = useState('transform duration-700 ease');
  const contentSpace = useRef(null);
  const content = message.type === 'gahyperparameters' ? <GAHyperparameters message={message} /> : message.type === 'gaEpoch' ? <GAEpoch message={message} /> : message.type === 'gaResults' ? <GAResult message={message} /> :'default';

  function toggleAccordion() {
    console.log('Toggle Accordions!');
    setActive((prevState) => !prevState);
    setHeight(active ? '0px' : `${contentSpace.current.scrollHeight}px`);
    setRotate(active ? 'transform duration-700 ease' : 'transform duration-700 ease rotate-180');
  }
  return (
    <div className="w-full flex flex-col">
      <button onClick={toggleAccordion} className="flex items-center p-2 justify-between w-full font-medium text-left text-gray-500 border border-b-0 border-gray-200 rounded-t-xl focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-800 dark:border-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
        <p className="inline-block text-footnote light">
          {
            message.type === 'gahyperparameters' ? 'GA Hyperparameters (Click here)'
            :((message.type === 'gaEpoch') ? `[${message.runid}] Epoch ${message.epoch} ======== Best Sharpe: ${message.population[0].sharpe} (Click here)`
            :((message.type === 'gaResults') ? `GA RESULT ======== BEST SHARPE: ${message.sharpe} (Click here)`
            :'default'))
          }
        </p>
        <svg data-accordion-icon className={`${rotate} inline-block w-6 h-6 shrink-0`} fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
      <div ref={contentSpace} style={{ maxHeight: `${height}` }} className="overflow-auto transition-max-height duration-700 ease-in-out">
        <div className="pb-10"><br />{content}</div>
      </div>
    </div>
  );
};

export default ConsoleAccordion;
