# polls
This is the repo for the UBI Center's [poll tracker](polls.ubicenter.org), an interactive web app to explore the state of public opinion on UBI across 58 different polls from 27 countries.

## Data
A google sheet with our data can be found [here](https://docs.google.com/spreadsheets/d/1ulqohI6YLYFsz3wm8f5j6BS_JVelu2Ea8SXXa-wwkhQ).

If you know of an interesting poll we might have missed, please submit an issue using [this template](https://github.com/UBICenter/polls/issues/new?assignees=&labels=new-poll&template=new-poll.md&title=Add+poll+from+%5Bpollster%5D+on+%5Bdates%5D).

## Installation
To install the app on your device, clone this repo. 

From the new directory, create a new conda environment and install dependencies with:
```python
conda env create --file environment.yaml
```
To run the app locally while in the directory root:
```python
python app.py
```


