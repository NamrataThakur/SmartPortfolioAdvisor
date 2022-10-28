import React, { useState, useEffect } from 'react';
import { MultiSelectComponent } from '@syncfusion/ej2-react-dropdowns';
import { TextBoxComponent } from '@syncfusion/ej2-react-inputs';
import { v4 as uuidv4 } from 'uuid';
import io from 'socket.io-client';
import { ConsoleAccordion } from '../components';
const config = require('../config');
const axios = require('axios');

const socket = io(config.flask.url);

const stocktickers = ['AAPL', 'MSFT', 'AMZN', 'TSLA', 'GOOG', 'BRK-B', 'UNH', 'JNJ', 'XOM', 'PG', 'META', 'JPM', 'NVDA', 'V', 'HD', 'CVX', 'ABBV', 'MA', 'PFE', 'LLY', 'PEP'];
const customga = config.flask.url+'/customga';

const CustomPortfolio = () => {
  const [messages, setMessages] = useState([]);
  const [post, setPost] = useState('');
  const [runid, setRunId] = useState('');
  const [reqid, setReqId] = useState(uuidv4());
  const [accordionStates, setAccordionStates] = useState({});

  const initialFormData = Object.freeze({
    reqId: reqid,
    stocktickers: [],
    popSize: 10,
    numEpoch: 40,
    selectionRate: 0.4,
    crossoverRate: 0.6,
    mutationRate: 0.6,
  });
  const [formData, updateFormData] = useState(initialFormData);

  useEffect(() => {
    let isMounted = true;
    if (isMounted) {
 socket.on('my_response', (data) => {
      	data.accordionId = uuidv4();
        setMessages((messages) => [data, ...messages]);
      });
}
    return () => {
      isMounted = false;
    };
  }, [socket]);

  const handleChange = (e) => {
    console.log(`handle change ${e.target.name} ${e.target.value}`);
    updateFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault(); // prevents url redirects after post submission
    setReqId(formData.reqId);
    setMessages([]);
    if (formData.stocktickers.length === 0) {
      setPost('Please select stock tickers!');
      return;
    }
    setPost('Setting up Custom GA run on server... ');
    axios.post(customga, formData, {
      headers: { 'Content-Type': 'application/json' },
    })
    .then((response) => {
      const serverResponse = response.data;
      const runidStr = serverResponse.split(':')[1].trim(); // will filter runs from server according to runid
      setPost(response.data);
      setRunId(runidStr);
    });
  };

  const handleStopRun = (e) => {
    e.preventDefault();
    if (runid.length > 0) {
      axios.post(stopcustomga, { runid }, {
        headers: { 'Content-Type': 'application/json' },
      })
      .then((response) => {
        setPost(response.data);
      });
    } else {
      setPost('No GA run at server to stop');
    }
  };
  return (
    <div>
      <div className="flex gap-5 border-b-1 border-color p-4 hover:bg-light-gray cursor-pointer  dark:hover:bg-[#42464D] justify-center">
        <p className="text-3xl font-semibold dark:text-gray-200 dark:bg-secondary-dark-bg w-full p-4 rounded-2xl text-center">Custom Portfolio</p>
      </div>
      <div className="gap-5 border-b-1 border-color p-4 hover:bg-light-gray cursor-pointer  dark:hover:bg-[#42464D] justify-self-stretch">
        <div id="stock-selection" className="overflow-y-scroll bg-white dark:text-gray-200 dark:bg-secondary-dark-bg p-2 rounded-2xl">
          <div className="w-full items-stretch justify-between items-center gap-2">
            <p className="text-xl font-semibold">Portfolio Optimizations Hyperparameters</p>
          </div>
          <div className="w-full items-stretch justify-between items-center gap-2" id="serverOutput">
            <p className="text-xl px-3 py-4 text-red-500 font-semibold">{ post }</p>
          </div>
          <div className="py-4 w-full justify-between items-center gap-2">
            <form>
              <div className="columns-3 w-full justify-between items-center gap-2">
                <label>Stocktickers:</label>
                <MultiSelectComponent
                  id="stocktickers"
                  Portfolio
                  Optimizations
                  Hyperparameters
                  name="stocktickers"
                  dataSource={stocktickers}
                  placeholder="Select Stocks"
                  onChange={handleChange}
                  className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                />
                <br />
                <br />
                <label htmlFor="popSize">Population Size:</label>
                <TextBoxComponent id="popSize" name="popSize" value="10" onChange={handleChange} />
                <br />
                <br />
                <label htmlFor="numEpoch">Number of Epochs:</label>
                <TextBoxComponent id="numEpoch" name="numEpoch" value="40" onChange={handleChange} />
                <br />
                <br />
                <label htmlFor="selectionRate">Selection Rate:</label>
                <TextBoxComponent id="selectionRate" name="selectionRate" value="0.4" onChange={handleChange} />
                <br />
                <br />
                <label htmlFor="crossoverRate">Crossover Rate:</label>
                <TextBoxComponent id="crossoverRate" name="crossoverRate" value="0.6" onChange={handleChange} />
                <br />
                <br />
                <label htmlFor="mutationRate">Mutation Rate:</label>
                <TextBoxComponent id="mutationRate" name="mutationRate" value="0.6" onChange={handleChange} />
                <br />
                <br />
              </div>
              <div className="columns-3 w-full justify-between items-center gap-2">
                <input
                  type="submit"
                  value="Submit"
                  onClick={handleSubmit}
                  className="px-6 py-2.5 bg-blue-600 text-white font-medium text-xs leading-tight uppercase rounded shadow-md hover:bg-blue-700 hover:shadow-lg focus:bg-blue-700 focus:shadow-lg focus:outline-none focus:ring-0 active:bg-blue-800 active:shadow-lg transition duration-150 ease-in-out"
                />
              </div>
            </form>
          </div>
        </div>
      </div>
      <div className="w-full flex gap-5 border-b-1 border-color p-4 hover:bg-light-gray cursor-pointer  dark:hover:bg-[#42464D] justify-center">
        <div id="console-output" className="w-full bg-white dark:text-gray-200 dark:bg-secondary-dark-bg p-2 rounded-2xl">
          <div className="flex justify-between items-center gap-2">
            <p className="text-xl font-semibold">Server output</p>
          </div>
          <div className="overflow-y-scroll overflow-x-scroll flex gap-5 border-b-1 border-color p-4 justify-center">
            <div>
              {
              messages.map((message) => {
                console.log(`=== DISPLAY === ${message.msgid} vs ${reqid}`);
                let accordionCurState = false;
                if (accordionStates[message.accordionId] !== undefined) accordionCurState = accordionStates[message.accordionId];
                if (message.msgid === reqid) {
                  return <ConsoleAccordion message={message} activeStateUpdateHandler={setAccordionStates} key={message.accordionId} />;
                }
              })
}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomPortfolio;
