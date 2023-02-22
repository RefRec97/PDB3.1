// ==UserScript==
// @name         Spio
// @namespace    http://tampermonkey.net/
// @version      3.3
// @description  try to take over the world!
// @author       Sc0t
// @match        https://pr0game.com/uni2/game.php?page=messages&category=0*
// @match        http://pr0game.com/uni2/game.php?page=messages&category=0*
// @match        http://37.221.67.168/uni2/game.php?page=messages&category=0*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=pr0game.com
// @updateURL    https://raw.githubusercontent.com/7Surfer/PDB3/main/scripts/spy.user.js
// @downloadURL  https://raw.githubusercontent.com/7Surfer/PDB3/main/scripts/spy.user.js
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        unsafeWindow
// ==/UserScript==

(function() {
    'use strict';

    function run(){

        var table = document.getElementsByTagName("table")[2]
        var messages = table.getElementsByClassName("messages_body")

        let data = GM_getValue("msgDatav3",{})
        for (let element of messages) {
            if(element.firstElementChild.firstElementChild.firstElementChild === null){
                continue
            }

            let msgFooter = element.firstElementChild.getElementsByClassName("spyRaportFooter")[0];
            let attackLink = msgFooter.getElementsByTagName('a')[0].href;
            let id = element.className.split("_")[1].split(" ")[0];

            let headderText = element.getElementsByClassName("spyRaportHead")[0].firstElementChild.text;
            let headderLink = element.getElementsByClassName("spyRaportHead")[0].firstElementChild.href;

            let timestamp = 0
            //Supported Languages:
            //German
            if (headderText.includes("Spionagebericht")) {
                timestamp = headderText.split(" am ")[1]
            }
            //English
            else if (headderText.includes("Spy Report")) {
                timestamp = headderText.split(" on ")[1]
            }
            else {
                console.log("Unsupported Language")
                continue
            }
            let tmp = {
                isMoon: attackLink.includes("planettype=3"), //planet or moon
                playerName: headderText.split("(")[1].split(")")[0].trim(),
                timestamp: timestamp,
                gal: Number(headderLink.split("galaxy=")[1].split("&")[0]),
                sys: Number(headderLink.split("system=")[1]),
                pos: Number(attackLink.split("planet=")[1].split("&")[0]),
                simu: msgFooter.getElementsByTagName('a')[1].href
        }
            if (!(id in data)){
                data[id] = tmp
            }
        }
        GM_setValue("msgDatav3",data)
        addButtons(data)
    }

    function clear(){
        //Clear Data
        let data = GM_getValue("msgDatav3",{})
        let amount = Object.keys(data).length
        data = {}
        GM_setValue("msgDatav3",data)

        //Set message
        document.getElementById("p-info").innerText = "Lokaler Speicher zurückgesetzt"
    }

    function addButtons(data){
        let html = "<button id='btn-clear'>Clear Table</button><input id='btn-dwn' type=button value=\"Download\"><p id='p-info'></p>"


        let htmlElement = document.createElement('div');
        htmlElement.innerHTML = html
        document.getElementsByClassName("wrapper")[0].insertBefore(htmlElement,document.getElementsByTagName("footer")[0])
        document.getElementById("btn-clear").addEventListener('click', () => clear());
        document.getElementById("btn-dwn").addEventListener('click', () => {
            let downloadData = {
                header: {
                    version: {
                        major: 3,
                        minor: 0,
                    }
                },
                data: data
            }
            downloadObjectAsJson(downloadData)
        });

        document.getElementById("p-info").innerText = "Anzahl: " + Object.keys(data).length
    }

    function downloadObjectAsJson(exportObj){
        let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
        let downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href",dataStr);
        downloadAnchorNode.setAttribute("download", "spy.json");
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }

    window.onload = run()
})();
