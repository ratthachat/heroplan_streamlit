# Quick Start

There are 2 hosts which you can play. These two hosts are free and can be stopped if nobody are used it for a while, and will be needed to restart manually.
* https://heroplan-explorer.streamlit.app/
* https://huggingface.co/spaces/Jung/ep_explorer

# Heroplan Explorer (Powered By Streamlit)

This is a simple Hero explorer on [Empire & Puzzles](https://forum.smallgiantgames.com/) that let you filter your interested heroes by class, speed, special skills and more!

Picture below shown an example when you want to see all heroes with are "Yellow (Holy), Barbarian with Hit-3 special skill" sorted by their power.</br>

<img src="https://github.com/ratthachat/heroplan_streamlit/blob/main/img/explorer/example1.png" width="80%" height="80%">

This repository applies the data for the amazing [Heroplan](https://github.com/GDIBass/heroplan_data/tree/main/) contributed by E&P community. If you spot some errors, please contribute to the original Heroplan repo above, and this repo will be updated accordingly.

Beside basic categories that you can filter such as **Class, Origin, Color and Speed**, you can filter heroes with free-text with **"Name", "Special Skill Category" and "Special Skill Text"**

**"Special Skill Category"** is manually defined by Heroplan community and may not be perfect, but it is quite comprehensive e.g. _"Hit 1", "Hit 3", "Hit All", "Cleanser", "Dispeller", "Healer", "Resurrect", etc._ while  **"Special Skill Text"** is what exactly written in the hero card. You can combine those two filters to get wanted results.

### Example 2: Hero with average speed, deal some damages and is cleanser
<img src="https://github.com/ratthachat/heroplan_streamlit/blob/main/img/explorer/example2.png" width="80%" height="80%">

### Example 3: (Mobile screenshot -- you can click filtering menu indicated by the red arrow) Hero with 2nd-costume who can Hit-all
<img src="https://github.com/ratthachat/heroplan_streamlit/blob/main/img/explorer/example_mobile_costume2.jpeg" width="70%" height="70%">

## Missing
* As the original Heroplan data does not provide "passive" ability, we don't have that information in this repo too
