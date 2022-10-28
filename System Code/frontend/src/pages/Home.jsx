import React, { useState, useEffect } from 'react';
import Axios from 'axios';
import { SparkLine, Pie, MyDayPicker } from '../components';
import { useStateContext } from '../contexts/ContextProvider';
import MyListGroup from '../components/MyListGroup';
import { logo } from '../data/logo';
const config=require('../config');

const findLogo = (stockName) => {
    for (let i = 0; i < logo.length; i++) {
        if (logo[i].stockName === stockName) {
            return logo[i].logo;
        }
    }
    return 'https://logo.clearbit.com/investor.fb.com';
};

const PickDayButton = ({ currentMode, currentColor, handleClick, isClicked }) => (
  <div className="w-28 border-1 border-color px-2 py-1 rounded-md">
    <MyDayPicker />
  </div>
);

const getStockportfolio = (date) => {
    Axios.post(config.database.url+'/stockportfolio', { date }).then((respose) => {
        const { data } = respose;
        // console.log(data);
        const stocktickers = data.stocktickers.replace('[', '').replace(']', '').replace(/\'/g, '').split(/,\s*/);
        // console.log(stocktickers);
        let chromosome = data.chromosome.replace('[', '').replace(']', '').replace(/\'/g, '').split(/\s+/);
        // console.log(chromosome)
        chromosome = chromosome.map((item) => Number(item));
        const res = [];
        for (let i = 0; i < stocktickers.length; i++) {
            if (chromosome[i] !== 0.0) {
                res.push({ x: stocktickers[i], y: chromosome[i], text: `${(chromosome[i] * 100).toFixed(2)}%` });
            }
        }
        console.log(res);
        return res;
    });
};

const Home = () => {
    const { currentColor, currentMode, handleClick, isClicked } = useStateContext();
    // const [todayStockportfolio,setTodayStockportfolio ] = useState(getStockportfolio("2022-08-22"));
    const [todayStockportfolio, setTodayStockportfolio] = useState([]);
    const [todayStockForecast, setTodayForecast] = useState([]);
    const [todaySharpe, setTodaySharpe] = useState(0);
    const [todayReturn, setTodayReturn] = useState(0);
    const [todayRisk, setTodayRisk] = useState(0);
    // useEffect(() => { setTodayStockportfolio(getStockportfolio("2022-08-22"))}, []);

    useEffect(() => {
        let isMounted = true;
        Axios.post(config.database.url+'/stockportfolio', { date: '2022-08-22' }).then((respose) => {
            if (isMounted) {
                const { data } = respose;
                const stocktickers = data.stocktickers.replace('[', '').replace(']', '').replace(/\'/g, '').split(/,\s*/);
                let chromosome = data.chromosome.replace('[', '').replace(']', '').replace(/\'/g, '').split(/\s+/);
                chromosome = chromosome.map((item) => Number(item));
                const res = [];
                setTodayRisk(Number(data.risk).toFixed(3));
                setTodaySharpe(Number(data.sharpe).toFixed(3));
                setTodayReturn(Number(data.return).toFixed(3));
                for (let i = 0; i < stocktickers.length; i++) {
                    if (chromosome[i] !== 0.0) {
                        res.push({ x: stocktickers[i], y: chromosome[i], text: `${(chromosome[i] * 100).toFixed(2)}%` });
                    }
                }
                setTodayStockportfolio(res);
            }
        });
        return () => { isMounted = false; };
    }, []);

    useEffect(() => {
        let isMounted = true;
        const stocks = [];
        for (let i = 0; i < todayStockportfolio.length; i++) {
            stocks.push(todayStockportfolio[i].x);
        }
        console.log(stocks);
        Axios.post(config.database.url+'/groupstockforecast', { stocks }).then((respose) => {
            if (isMounted) {
                const { data } = respose;
                console.log(data);
                const date = data.date.split(',');
                const price = data.price.split(',');
                console.log(date.length);
                console.log(price.length);
                const temp = [];
                for (let i = 0; i < date.length; i++) {
                    temp.push({ x: i % 20, date: new Date(date[i]), price: Number(price[i]).toFixed(2) });
                }
                setTodayForecast(temp);
                console.log(todayStockForecast);
            }
        });
        return () => { isMounted = false; };
    }, [todayStockportfolio]);

    const recommendDegree = (num) => {
        // if (num >= 0.2) {
        //    return <div className='text-md font-bold text-green-400'>{`Hightly Recommend : ${num.toFixed(3)}`}</div>;
        // }
        // else if (num >= 0.1) {
        //    return <div className='text-md font-bold text-yellow-400'>{`Recommend : ${num.toFixed(3)}`}</div>;
        // }
        // else {
        //    return <div className='text-md font-bold text-red-600'>{`Not Recommend : ${num.toFixed(3)}`}</div>;
        // }
        if (num >= 0.2) {
            return <div className="text-md font-bold text-green-400">{num.toFixed(3)}</div>;
        }
        if (num >= 0.1) {
            return <div className="text-md font-bold text-yellow-400">{num.toFixed(3)}</div>;
        }

            return <div className="text-md font-bold text-red-600">{num.toFixed(3)}</div>;
    };
    return (
      <div className="mt-12">
        <div className="flex gap-5 border-b-1 border-color p-4 hover:bg-light-gray cursor-pointer  dark:hover:bg-[#42464D] justify-center">
          <p className="text-3xl font-semibold dark:text-gray-200 dark:bg-secondary-dark-bg w-full p-4 rounded-2xl text-center">{`Portfolio Recommendation (${new Date().toDateString().slice(4)})`}</p>
        </div>
        <div className="flex gap-5 border-b-1 border-color p-4 hover:bg-light-gray cursor-pointer  dark:hover:bg-[#42464D] justify-center">
          <div className="bg-white dark:text-gray-200 dark:bg-secondary-dark-bg p-2 rounded-2xl">
            <div className="flex justify-between items-center gap-2">
              <p className="text-xl font-semibold">Recommendation</p>
              {/* <DropDown currentMode={currentMode} /> */}
              {/* <MyDayPicker currentMode={currentMode} currentColor={currentColor} handleClick={handleClick} isClicked={isClicked} /> */}
            </div>
            <div className="mt-10 w-72 md:w-400">
              {todayStockportfolio.sort((a, b) => {
                                if (a.y === b.y) {
                                    return 0;
                                }

                                    return (a.y < b.y) ? 1 : -1;
                            }).map((item) => (
                              <div key={item.x} className="flex justify-between mt-4">
                                <div className="flex gap-4">
                                  <button
                                    type="button"
                                    className="text-2xl rounded-lg p-1 hover:drop-shadow-xl"
                                  >
                                    <div className="flex w-10">
                                      <img src={findLogo(item.x)} />
                                    </div>
                                  </button>
                                  <div>
                                    <p className="text-md font-semibold">{item.x}</p>
                                    <p className="text-sm text-gray-400">{item.x}</p>
                                  </div>
                                </div>
                                {/* <p className={`text-${item.pcColor}`}>{item.amount}</p> */}
                                <p className="text-red-600">{recommendDegree(item.y)}</p>
                              </div>
                        ))}
            </div>
          </div>
          <div className="bg-white dark:text-gray-200 dark:bg-secondary-dark-bg p-6 rounded-2xl w-96 md:w-760">
            <div className="flex justify-between items-center gap-2">
              <p className="text-xl font-semibold">Portfolio Summary</p>
            </div>
            <MyListGroup todaySharpe={todaySharpe} todayReturn={todayReturn} todayRisk={todayRisk} />
            <div className="md:w-full overflow-auto">
              <Pie id="pie-chart" data={todayStockportfolio} legendVisiblity={false} height="400px" />
              {/* <StockChart /> */}
            </div>
          </div>
        </div>
        <div className="flex flex-wrap lg:flex-nowrap justify-center ">
          <div className="flex m-3 flex-wrap justify-center gap-2 items-center">
            {todayStockportfolio.slice(0, Math.ceil(todayStockForecast.length / 20)).map((item, i) => (
              <div key={item.x} className="bg-white h-44 dark:text-gray-200 dark:bg-secondary-dark-bg md:w-56  p-4 rounded-2xl ">
                <div className="flex">
                  <div className="text-md font-semibold">{item.x}</div>
                  <div className="text-sm text-gray-400  mt-1">{` (${item.x})`}</div>
                </div>
                {/* <div>
                                {recommendDegree(item.y)}
                            </div> */}
                <div className="pt-4">
                  <SparkLine currentColor={currentColor} id={`sparkline-${item.x}`} type="Line" height="60px" width="160px" data={todayStockForecast.slice(10 + i * 20, 20 + i * 20)} color={currentColor} />
                </div>
              </div>

                    ))}
          </div>
        </div>
      </div>
    );
};

export default Home;
