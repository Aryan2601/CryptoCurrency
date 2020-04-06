// mycoin ICO

// version of compiler

pragma solidity ^0.4.11;


contract mycoin_ico {
    
    //Introducing max number of mycoins for sealed
    uint public max_mycoins = 1000000;
    
    //Introducing the USD to mycoin conversion rate 
    uint public usd_to_mycoins = 1000;
    
    //Introducing the maximum numbers of mycoins that have been bought by the investors
    uint public total_mycoins_bought = 0;
    
    // Mapping from the investor address to its equity in mycoins and USD 
    //mapping is like function in which the data of mapping is stored
    mapping(address => uint) equity_mycoins; //specifying here type of output that is integer as uint
    mapping(address => uint) equity_usd;
    
    //checking if an investor can buy mycoins 
    modifier can_buy_mycoins(uint usd_invested){
        
        
        require(usd_invested * usd_to_mycoin + total_mycoins_bought <= max_mycoins);
        
        
        
    }
    
    //Getting the equity on mycoins of an investor 
    function equity_in_mycoins(address investor) external constant returns (uint){
        return equity_mycoins[investor];
    }
    // Getting thr equity in USD of an investor
    function equity_in_usd(address investor) external constant returns (uint){
        return equity_usd[investor];  
    }
    
    //Buying mycoin function to buy mycoins
    
    function buy_mycoins(address investor,uint usd_invested) external 
    can_buy_mycoins(usd_invested){
        mycoins_bought = usd_invested * usd_to_mycoins;
        equity_mycoins[investor] += mycoins_bought;
        equity_usd[investor] = equity_mycoins[investor] / 1000;
        total_mycoins_bought += mycoins_bought;
    }
    
    //function for selling mycoins
    function sell_mycoins(address investor,uint mycoins_sold) external {
        equity_mycoins[investor] -= mycoins_sold;
        equity_usd[investor] = equity_mycoins[investor] / 1000;
        total_mycoins_bought -= mycoins_sold ;
        
    }
}
