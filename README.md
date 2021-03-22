# Ascendex Futures Api Demo V2

## Command line Tools

- **Get Account Info**
```
python3 cli/get-account-info.py --config sample-conf.yaml
```
- **Get Free Margin**
```
python3 cli/get-free-margin.py --config sample-conf.yaml
```
- **Place Batch Orders**
```
python3 cli/place-order-batch.py --config sample-conf.yaml --symbol BTC-PERP --price 34000,35000 --qty 0.1,0.2 --order-type limit --side buy 
```
- **Cancel Batch Orders**
```
python3 cli/cancel-order-batch.py --config sample-conf.yaml --symbol BTC-PERP --order-id a177c29e4064U6846912707dVeUxlVyA,a177c29e4064U6846912707dVeUxlVyB 
```
- **Cancel All Open Orders**
```
python3 cli/cancel-all-open-order.py --config sample-conf.yaml --botname ascendex-sandbox --verbose 
```
- **Query Order By ID**
```
python3 cli/lookup-futures-orders.py --config sample-conf.yaml --order-id a177c29e4064U6846912707dVeUxlVyA 
python3 cli/lookup-futures-orders.py --config sample-conf.yaml --order-id a177c29e4064U6846912707dVeUxlVyA, 
python3 cli/lookup-futures-orders.py --config sample-conf.yaml --order-id a177c29e4064U6846912707dVeUxlVyA,a177c29e4064U6846912707dVeUxlVyB 
```
- **List Current History Orders**
```
python3 cli/get-curr-order-hist.py --config sample-conf.yaml --symbol BTC-PERP --n 20 --executed-only 
```
- **Close All Position**
```
python3 cli/close-all-position.py --config sample-conf.yaml --botname ascendex-sandbox  
```


