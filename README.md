## SECTION 1 : PROJECT TITLE
## SmartPortfolioAdvisor

<img src="./img/SmartPortfolioAdvisor.png"
     style="float: left; margin-right: 0px;" />

---

## SECTION 2 : EXECUTIVE SUMMARY
There is a common saying that monkeys make better fund managers than humans. This was based on a series of experiments run, the most famous one being a Chimpanzee, Raven,  who threw 10 darts to pick stocks from a basket of 133 internet companies. Her stock picks delivered a 213 per cent gain in 1999, outperforming more than 6,000 professional brokers on Wall Street.

How can the average investor make quality investment decisions? Other than cherry picking stocks, there are many options in the market today, from mutual funds, to index investing and roboadvisories. One way to assess a portfolio’s health is by measuring its returns relative to its risk, to understand if the portfolio is generating a reasonable return for the risk it is assuming. The Sharpe Ratio, proposed by William Sharpe, is one of the most popular methods that is used to measure risk adjusted relative returns in Modern Portfolio Theory.

In this project, we demonstrate the use of Sharpe Ratio as a measure of portfolio fitness to evolve a portfolio of stocks using Genetic Algorithm. We also apply LSTM modeling to forecast future stock prices.


---

## SECTION 3 : CREDITS / PROJECT CONTRIBUTION

| Official Full Name  | Student ID | Work Items | Email |
| :------------ |:---------------:| :-----| :-----|
| Namrata Thakur | A0261619B | 1. Integration 2. Setup guide writing 3. Video creation | e0983013@u.nus.edu |
| Ouyang Hui | A0261875U | 1. LSTM model 2. Project report writing 3. Bug fixing 4. Video creation| e0983269@u.nus.edu |
| See Jia Fong Grace | A0261797M | 1.GA Algo 2. Project report writing 3. Bug fixing 4. Integration & deployment 5. Video Creation | e0983191@u.nus.edu |
| Wang Zhipeng | A0261980Y | 1. Frontend Lead 2. Project report writing | e0983013@u.nus.edu  |

---

## SECTION 4 : VIDEO OF SYSTEM MODELLING & USE CASE DEMO

Link to video

---

## SECTION 5 : USER GUIDE

`Refer to User Guide at Github Folder: ProjectReport`

### To run the system in local machine:
#### Requirements


> Clone repo
>
> 
> Install dependencies
>
> $ npm install
>
> run server
>
> $ npm start


---
## SECTION 6 : PROJECT REPORT / PAPER

`Refer to project report at Github Folder: ProjectReport`

**Sections for Project Report**
- Introduction
  - Business Value
  - Project Aim
- System Architecture
  - Deployment
- System Features
  - Stock Data Retrieval
  - Portfolio Recommendation of the day (based on Daily GA Run)
  - Custom Portfolio Recommendation (based on Custom GA Run)
  - Stock Price Forecasting
  - Historical Portfolio Recommendations
  - Financial News
- GA Algorithm for Portfolio Recommendation
- Knowledge Identification
    - Fitness Function Definition
    - Data specification
    - Hyperparameter specification
  - Knowledge specification
  - Chromosome
  - Fitness Value (Sharpe) Computation
    - Computation of Daily Return
    - Computation of Annualized Daily Return
    - Computation of Annualized Portfolio Variance
    - Computation of Risk Free Rate
    - Computation of Annual Sharpe Ratio
  - Population Selection and Generation
  - Crossover
  - Mutation
  - Termination Criteria
    - Single run termination criteria (convergence or max epoch)
    - Multi-run termination criteria (Sharpe Ratio 2, recursion depth of 5)
  - Knowledge Refinement
    - Algorithm Tuning
    - Key Performance Indicators
    - Run time optimizations
  - Limitations and Improvements
    - Too Slow!
    - Overly-dynamic portfolio recommendations
    - Only Linux
- LSTM Model for Stock Price Forecasting
  - Knowledge Identification
  - Knowledge Specification
    - Data preprocessing
    - Dataset creation
  - Knowledge Refinement
  - Limitations and improvements
- Conclusion
- References

---
## SECTION 7 : Miscellaneous

`Refer to Github Folder: Miscellaneous`


---

**This [Machine Reasoning (MR)](https://www.iss.nus.edu.sg/executive-education/course/detail/machine-reasoning "Machine Reasoning") course is part of the Analytics and Intelligent Systems and Graduate Certificate in [Intelligent Reasoning Systems (IRS)](https://www.iss.nus.edu.sg/stackable-certificate-programmes/intelligent-systems "Intelligent Reasoning Systems") series offered by [NUS-ISS](https://www.iss.nus.edu.sg "Institute of Systems Science, National University of Singapore").**

**Lecturer: [GU Zhan (Sam)](https://www.iss.nus.edu.sg/about-us/staff/detail/201/GU%20Zhan "GU Zhan (Sam)")**

[![alt text](https://www.iss.nus.edu.sg/images/default-source/About-Us/7.6.1-teaching-staff/sam-website.tmb-.png "Let's check Sam' profile page")](https://www.iss.nus.edu.sg/about-us/staff/detail/201/GU%20Zhan)

**zhan.gu@nus.edu.sg**


