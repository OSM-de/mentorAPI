var i18u = function(lang="en", langRef={}) {
	/*
	ISO 639-1 format description:
		https://en.wikipedia.org/wiki/ISO_639-1
	
	Object type of `lang`:
		String
	
	Default value of `lang`:
		en
	
	Example of `lang`:
		en
	
	Object type of `availableLangPages`:
		JSON
	
	Syntax of `langRef`:
		{"<language code in ISO 639-1 format>": "<JSON object>"}
	
	Example of `langRef`:
		{
		"en":
			{
			"PAGEHEADERTEXT": "My first page",
			"PAGESUBTITLE": "Now I am finally online"
			},
		"de":
			{
			"PAGEHEADERTEXT": "Meine erste Seite",
			"PAGESUBTITLE": "Nun bin ich endlich online"
			}
		}
	*/
	
	let dir = new Object();
	
	dir.langRef = langRef;
	
	function getText(address=undefined) {
		if (address == undefined) {
			return dir.langRef[lang]
		}
		return dir.langRef[lang][address]
	}
	dir.getText = getText;
	
	async function loadLang(url, callback=function(d) {return 0}) {
		if (lang in dir.langRef == false) {
			if (url == undefined) {
				url = lang + ".json"
			}
			let result;
			let response = await fetch(url, {"method": "GET", "cache": "force-cache"});
			result = await response.json();
			dir.langRef[lang] = result;
		}
		
		if (lang in dir.langRef == true) {
			console.info("i18u:\nLanguage data for language '" + lang + "' has been loaded!");
			callback(getText());
		} else {
			console.error("i18u:\nLanguage data for language '" + lang + "' couldn't be loaded!");
			callback({"i18u_error": "LANGNOTLOADED"});
		}
		
	}
	dir.loadLang = loadLang;
	
	return dir;
}

function i18u_redirect(availableLangPages, fallback) { //javascript redirect to the appropriate localized site
	/*
	ISO 639-1 format description:
		https://en.wikipedia.org/wiki/ISO_639-1
	
	Object type of `availableLangPages`:
		JSON
	
	Syntax of `availableLangPages`:
		{"<language code in ISO 639-1 format>": "<url to the JSON file containg the text in that specified language for the UI>"}
	
	Example of `availableLangPages`:
		{
		"en": "/en.json",
		"de": "/de.json",
		"fr": "/fr.json",
		"es": "/es.json"
		}
	
	Object type of `fallback`:
		String
	
	Example of `fallback`:
		en
	*/
	
	let languageOfUser = navigator.language || navigator.userLanguage;
	let languageOfUser_simplified = languageOfUser.split("-")[0];
	
	for (let langcode of [languageOfUser, languageOfUser_simplified, fallback]) {
		if (availableLangPages[langcode]) {
			location.href = availableLangPages[langcode];
			return "LOCALIZED";
		}
	}
	
	console.error("i18u_redirect:\nlocalized site for the users' language couldn't be found!");
	console.error("i18u_redirect:\nEven a localized site for the fallback language '" + fallback + "' couldn't be found!");
	return "NOLOCALIZATION";
}
