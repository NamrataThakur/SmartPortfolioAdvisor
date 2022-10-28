import React, { useEffect, useState } from 'react';
import * as ReactDOM from 'react-dom';
// import { chartData } from './datasource.ts';
import Axios from 'axios';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
  } from 'chart.js';
  import { Line } from 'react-chartjs-2';
import { lineCustomSeries, searchData } from '../../data/dummy';
import { useStateContext } from '../../contexts/ContextProvider';

const config=require('../../config');
const StockChart = () => {
    const { stockforecast, setStockforecast } = useStateContext();
    const [date, setDate] = useState([]);
    const [price, setPrice] = useState([]);
    useEffect(() => {
        let isMounted = true;
        console.log(`stockforecast ${stockforecast}`);
        console.log(`typeof ${typeof (stockforecast)}`);
        let symbol = 'NONE';
        for (let i = 0; i < searchData.length; i++) {
          if (searchData[i].StockName === stockforecast) {
            symbol = searchData[i].symbol;
            break;
          }
        }
        console.log(`symbol ${symbol}`);
        Axios.post(config.database.url+'/stockforecast', { stock: symbol }).then((respose) => {
            if (isMounted) {
                const { data } = respose;
                console.log(data);
                setDate(data.date.split(','));
                setPrice(data.price.split(','));
            }
        });
        return () => { isMounted = false; };
    }, [stockforecast]);

    ChartJS.register(
        CategoryScale,
        LinearScale,
        PointElement,
        LineElement,
        Title,
        Tooltip,
        Legend,
      );
      // console.log(price)
      const options = {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: `${stockforecast}'s stock price for the next four weeks`,
          },
        },
      };

      const labels = date;

      const data = {
        labels,
        datasets: [
          {
            label: stockforecast,
            data: price.map((v, i) => { if (i <= 10) { return v; } return null; }),
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
          },
          {
            label: `${stockforecast} forecast`,
            data: price.map((v, i) => { if (i < 10) { return null; } return v; }),
            borderColor: 'rgb(3, 190, 252)',
            backgroundColor: 'rgba(3, 190, 252, 0.5)',
            borderDash: [5, 10, 15],
          },
        ],
      };
    // console.log(chartData)
    return (
      <Line options={options} data={data} />
    );
};

export default StockChart;
