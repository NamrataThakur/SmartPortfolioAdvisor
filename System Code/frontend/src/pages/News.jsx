import React, { useEffect, useState } from 'react';
import { useStateContext } from '../contexts/ContextProvider';
import { userProfileData } from '../data/userData';
import { companyInfo } from '../data/dummy';
import { New } from '../components';
import newsImage from '../data/news.jpg';

const axios = require('axios');

const News = () => {
  const { currentColor, currentMode } = useStateContext();
  const [news, setNews] = useState([]);
  useEffect(() => {
    const options = {
      method: 'GET',
      url: 'https://bing-news-search1.p.rapidapi.com/news',
      params: { category: 'business', mkt: 'en-US', safeSearch: 'Off', textFormat: 'Raw' },
      headers: {
        'X-BingApis-SDK': 'true',
        'X-RapidAPI-Key': '6be3939a73msh413d424fc2d04c4p15ba7bjsnd28f29cebde3',
        'X-RapidAPI-Host': 'bing-news-search1.p.rapidapi.com',
      },
    };

    axios.request(options).then((response) => {
      const values = response.data.value;
      for (let i = 0; i < values.length; i++) {
        console.log(values[i]);
      }
      setNews(response.data.value);
    }).catch((error) => {
      console.error(error);
    });
  }, []);
  return (
    <div className="m-2 md:m-4 mt-12 p-2 md:p-4">
      <div className="flex justify-center text-7xl italic gap-3">
        <div className={currentMode === 'Dark' ? 'text-white' : 'text-black'}>
          Financial News
        </div>
      </div>
      <div className="flex gap-5 border-b-1 border-color p-16 pt-20 hover:bg-light-gray cursor-pointer  dark:hover:bg-[#42464D] justify-center">
        <div className="bg-white dark:text-gray-200 dark:bg-secondary-dark-bg p-2 rounded-2xl">
          {news.map((item) => (
            <div key={item.name}>
              <div className="bg-white h-44 dark:text-gray-200 dark:bg-secondary-dark-bg p-4 rounded-2xl flex w-full">
                {/* {item.name} */}
                <New
                  datePublished={item.datePublished}
                  description={item.description}
                  image={item.image !== undefined ? item.image.thumbnail.contentUrl : newsImage}
                  name={item.name}
                  url={item.url}
                />
              </div>
              <div className="relative flex py-5 items-center">
                <div className="flex-grow border-t border-gray-400" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default News;
