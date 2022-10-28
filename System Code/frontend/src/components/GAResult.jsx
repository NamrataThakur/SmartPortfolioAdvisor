import React from 'react';

const GAResult = ({ message }) => (
  <div>
    <p> Run ID: {message.runid} </p>
    <p> Sharpe Ratio: {message.sharpe} </p>
    <table className="shadow-lg bg-white">
      <thead>
        <tr>
          {message.stocktickers.map((ticker) => <th key={Math.random()} className="bg-blue-100 border text-left px-2 py-1">{ticker}</th>)}
        </tr>
      </thead>
      <tbody>
          <tr key={Math.random()}>
            {message.allocPerc.map((allocPercVal) => <td key={Math.random()} className="bg-blue-100 border text-left px-2 py-1">{allocPercVal.toFixed(3)}</td>)}
          </tr>
            
      </tbody>
    </table>
    <br />
  </div>
  );

export default GAResult;
