const axios = require('axios');
const config = require('config');
const date = '2022-08-22';
axios.put(config.database.url+'/stockportfolio', { date })
.then((response) => {
    const { data } = response;
    console.log(data);
});
