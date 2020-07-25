var languageOfUser, lang, smartLocation, smartContact, writingTimeout;
var queue = [];
var url = "http://localhost:9090"
var langRef = {};
var API = mentorAPI(url);
var smartField = smartTypingField();
var loggedIn = false;
var hasProfile = false;
var userprofile = {};
var contactmethods = [];
var regiocodeAutocompletionCache = {};
var usersearchCache = {};

function notifyUser(m) {
	function trigger(message) { // Triggers the yellow rounded message popup
		setTimeout(function() {
			document.getElementById("message").innerHTML = message;
			document.getElementById("notificationArea").style.display = "block"; //Display the message
			setTimeout(function() {
				document.getElementById("notificationArea").style.display = "none"; //Wait for 3sec and then close the popup
			}, 3000);
		}, 500);
	}
	
	if (m.info) {
		if (m.info == "SUCCESS") { trigger(lang.getText().STATE_SUCCESS); }
		else if (m.info == "NOPROFILE") { trigger(lang.getText().STATE_NOPROFILE); }
	} else if (m.error) {
		if (m.error == "LOGINREQUIRED") { trigger(lang.getText().STATE_LOGINREQUIRED); }
		else if (m.error == "NOPROFILE") { trigger(lang.getText().STATE_NOPROFILE); }
		else if (m.error == "LOCATIONREQUIRED") { trigger(lang.getText().STATE_LOCATIONREQUIRED); }
	}
}

function createoviewprofile() {
	if (hasProfile) {
		resetmain();
		let elem = document.getElementById("profile");
		let generalFields = {"displayname": "text", "location": "text", "about": "hide", "imageurl": "hide", "available": "checkbox:yes,no"}
		let outGeneral = "";
		let outContact = "";
		elem.innerHTML = "";
		for (let i in userprofile) {
			let value = userprofile[i];
			
			if (i == "id") {
				continue;
			}
			if (value == null) {
				value = ""
			}
			
			if (generalFields[i] != undefined) {
				let type = generalFields[i];
				
				if (type == "text") {
					outGeneral += `<div class='datafield'><label>${lang.getText()["DATAFIELD_" + i.toUpperCase()]}:<br/><input type='text' id='userdata_${i}' value='${value}' /></label></div>`;
				} else if (type == 'multitext') {
					outGeneral += `<div class='datafield'><label>${lang.getText()["DATAFIELD_" + i.toUpperCase()]}:<br/><textarea id='userdata_${i}' value='${value}' ></textarea></label></div>`;
				} else if (type.startsWith("checkbox:")) {
					let out = `<div class='datafield'><label>${lang.getText()["DATAFIELD_" + i.toUpperCase()]}:<br/><select id='userdata_${i}'>`;
					let options = type.replace("checkbox:", "").split(",")
					
					for (let option of options) {
						out += `<option value='${option}'>${lang.getText()["DATAFIELD_" + i.toUpperCase() + "_" + option.toUpperCase()]}</option>`;
					}
					
					out += "</select></label></div>";
					outGeneral += out;
				}
			} else {
				outContact += `<div class='datafield'><label>${lang.getText()["DATAFIELD_" + i.toUpperCase()]}:<br/><input type='text' id='userdata_${i}' value='${value}' /></label></div>`;
			}
		}
		
		elem.innerHTML = "<div class='generalprofile profilesection'>" + outGeneral + "</div><div class='contactprofile profilesection'>" + outContact + "</div><button onclick='saveProfile();'>" + lang.getText().BTN_PROFILE_SAVE + "</button> <i>" + lang.getText().OR + "</i><hr/><div class='removeProfile profilesection'><p>" + lang.getText().PROFILE_REMOVE + "</p><button class='removeprofilebtn' onclick='API.removeProfile(notifyUser)' >" + lang.getText().BTN_PROFILE_REMOVE + "</button></div>";
		elem.style.display = "block";
	} else {
		API.createProfile(notifyUser);
		init();
	}
}

function saveProfile() {
	let out = {};
	
	for (let i in userprofile) {
		console.log(i);
		let child = document.getElementById("userdata_" + i);
		
		if (child != undefined || child != null) {
			out[i] = child.value;
		}
	}
	
	API.changeProfile(out, notifyUser);
	
	resetmain();
}

function hideSearchBox(e) {
	let elems = document.getElementsByClassName("searchresult");
	for (let elem of elems) {
		elem.style = "";
	}
	document.removeEventListener("click", hideSearchBox);
}
function createSearchResultBox(smartId, resultset) {
	let elem = document.getElementById(smartId + "_searchresult");
	elem.innerHTML = ""; //clean it
	
	let lis = [];
	let index = 0;
	for (let result of resultset) {
		let li = document.createElement("li");
		let t = document.createTextNode(result);
		
		li.appendChild(t);
		li.id = smartId + "_searchresult_" + String(index);
		index += 1;
		li.addEventListener("click", function(e) {
			//emulating the 'onkeydown' event
			e = new Object();
			e.preventDefault = function() { return 0 };
			e.target = document.getElementById(smartId + "_searchbox");
			e.key = ",";
			e.code = ",";
			
			document.getElementById(smartId + "_searchbox").value = li.innerHTML;
			smartTypingFields_pressedOnSearchbox(e, smartId);
			hideSearchBox(e);
		});
		lis.push(li);
	}
	
	for (let li of lis) {
		elem.appendChild(li);
	}
	elem.style.display = "block";
	document.addEventListener("click", hideSearchBox);
}

function regiocodeAutocompletion() {
	let regiocode = [];
	let body = {}
	for (let part of document.getElementById(smartLocation + "_parts").children) {
		regiocode.push(part.innerText.replace("x", ""));
	}
	
	let value = document.getElementById(smartLocation + "_searchbox").value;
	body[value] = regiocode;
	
	if (regiocodeAutocompletionCache[value] == undefined) {
		API.searchForRegion(body, function(resp) {
			let out = [];
			let searchWhat = "";
			let searchIn = "";
			
			for (var i in resp) {
				searchWhat = i;
				searchIn = resp[i];
				break;
			}
			
			regiocodeAutocompletionCache[searchWhat] = searchIn;
			regiocodeAutocompletion();
			}
		);
		return 0;
	}
	
	createSearchResultBox(smartLocation, regiocodeAutocompletionCache[value]);
}

function contactAutocompletion() {
	let elem = document.getElementById(smartContact + "_searchbox");
	let out = [];
	
	for (let contact of contactmethods) {
		if (contact.indexOf(elem.value) > -1) {
			out.push(contact);
		}
	}
	
	createSearchResultBox(smartContact, out);
}

function searchusers() {
	let elem = document.getElementById("userlist");
	let location = document.getElementById(smartLocation + "_parts");
	let contact = document.getElementById(smartContact + "_parts");
	let outLoc = [];
	let body = {};
	let cacheid = []
	
	
	resetmain();
	
	for (let i of location.children) {
		outLoc.push(i.innerText.replace("x", ""));
	}
	body["location"] = outLoc.join(",");
	cacheid.push(outLoc.join(","));
	
	for (let i of contact.children) {
		body[i.innerText.replace("x", "")] = "";
		cacheid.push(i.innerText.replace("x", ""));
	}
	
	cacheid = cacheid.join(",")
	
	function callb(resp) {
		usersearchCache[cacheid] = resp;
		let users = resp.resultset;
		let urlhandlers = {"matrix": "https://matrix.to/#/#", "telegram": "https://t.me/", "email": "mailto:"}
		let entries = [];
		for (let i in users) {
			let info = {};
			let info_text = [];
			let user = users[i];
			for (let u in user) {
				if (user[u] != undefined || user[u] != null || user[u] != "") {
					info[u] = user[u];
				}
			}
			for (let u in info) {
				let title = u.charAt(0).toUpperCase() + u.slice(1);
				if (u == "id" || u == "available" || u == "location" || u == "displayname" || u == "imageurl") {
					continue;
				}
				if (u == "email") {
					info_text.push("<a href='mailto:" + info[u] + "'>E-Mail</a>");
				} else {
					info_text.push("<a target='_blank' href='" + urlhandlers[u]  + info[u] + "'>" + title + "</a>");
				}
			}
			entries.push("<div class='profilefield'><img class='avatar' src='" + info["imageurl"] + "' onerror='errorLoadingImage(event);' /><h3>" + info["displayname"] + "</h3><div class='info'><span>" + info_text.join(" &nbsp; ") + "</span></div></div>");
		}
	elem.innerHTML = entries.join("");
	elem.style.display = "flex";
	}
	
	if (usersearchCache[cacheid] == undefined) { API.searchAround(body, callb); }
	else { callb(usersearchCache[cacheid]); }
}
function errorLoadingImage(elem) {
	elem = elem.target;
	if (elem.getAttribute("errored") == undefined) {
		elem.setAttribute("errored", true);
		elem.src = "images/humanface.svg";
	}
}
function changeUIText(UItext) {
	let createoviewprofile = document.getElementById("createoviewprofile");
	let loginologout = document.getElementById("loginologout");
	let navimg = document.getElementsByClassName("menu")[0];
	
	resetmain();
	
	if (loggedIn) {
		navimg.src = userprofile["imageurl"];
		navimg.addEventListener("error", errorLoadingImage);
		loginologout.innerHTML = lang.getText().LNK_LOGOUT;
		loginologout.href = url + "/logout";
		createoviewprofile.style.display = "block";
		if (hasProfile) {
			createoviewprofile.innerHTML = lang.getText().LNK_VIEWPROFILE;
			createoviewprofile.classList.remove("red");
			createoviewprofile.href = "#yourprofile";
		} else {
			createoviewprofile.innerHTML = lang.getText().LNK_CREATEPROFILE;
			createoviewprofile.classList.add("red");
			createoviewprofile.href = "#";
		}
	} else {
		navimg.src = "images/menu.svg";
		loginologout.innerHTML = lang.getText().LNK_LOGIN;
		loginologout.href = "#";
		loginologout.onclick = function() {API.loginWith("osm")};
		createoviewprofile.style.display = "none";
	}
	document.getElementById("smartLocation").innerHTML = "";
	smartLocation = smartField.createSearch(document.getElementById("smartLocation"), lang.getText().SEARCH_LOCATION, lang.getText().SEARCH_LOCATION_RESULT, lang.getText().SEARCH_LOCATION_PARTS);
	
	document.getElementById("smartContact").innerHTML = "";
	smartContact = smartField.createSearch(document.getElementById("smartContact"), lang.getText().SEARCH_CONTACT, lang.getText().SEARCH_CONTACT_RESULT, lang.getText().SEARCH_CONTACT_PARTS);
	
	document.getElementById("usersearch").innerHTML = lang.getText().BTN_USERSEARCH;
	
	setTimeout(function() {
		document.getElementById(smartLocation + "_searchbox").addEventListener("keydown", function(e) {
			clearTimeout(writingTimeout);
			if (document.getElementById(smartLocation + "_searchbox").value.length > 1) {
				writingTimeout = setTimeout(regiocodeAutocompletion, 200);
			}
		});
		//regiocodeAutocompletion();
		document.getElementById(smartContact + "_searchbox").addEventListener("keydown", function(e) {
			clearTimeout(writingTimeout);
			if (document.getElementById(smartContact + "_searchbox").value.length > 1) {
				writingTimeout = setTimeout(contactAutocompletion, 200);
			}
		});
	
	}, 500); //HACK: gives the DOM time to refresh. It is a poor design decision that the DOM and JS code are on the same thread
	
	for (let i of queue) {
		let func = i[0];
		let value = i[1];
		func(value);
	}
	queue = [];
}

function changeLang() {
	let hash = location.hash.split("&");
	
	for (let i in hash) {
		let pair = hash[i].split("=");
		if (pair[0] == "lang") {
			languageOfUser = pair[1];
			break;
		}
	}
	
	if (languageOfUser == undefined) {
		languageOfUser = navigator.language || navigator.userLanguage;
		languageOfUser = languageOfUser.split("-")[0];
	}
	
	lang = i18u(languageOfUser, langRef);
	lang.loadLang("../json/" + languageOfUser + ".json", changeUIText);
	langRef = lang.langRef;
	
	window.addEventListener("hashchange", hashChange);
}
function resetmain() {
	for (let i of ["profile", "userlist"]) { //reset view
		document.getElementById(i).innerHTML = "";
		document.getElementById(i).style = "";
	}
}
function init() {
	window.removeEventListener("hashchange", hashChange);
	
	API.myuser(function(state) {
		if (!state.error) { //user is logged in
			loggedIn = true;
			if (!state.info) { //user has profile
				hasProfile = true;
			}
			userprofile = state;
		}
		changeLang();
	});
	
	if (contactmethods.length == 0) {
		API.contactmethods(function(resp) {contactmethods = resp.split(",")});
	}
	changeLang();
	resetmain();
}

function hashChange(e) {
	let hash = location.hash;
	
	let triggers = {"yourprofile": createoviewprofile};
	let queue = [];
	hash = hash.split("&");
	
	for (let i in hash) {
		if (hash[i].indexOf("=") > -1) {
			let value = hash[i].split("=");
			if (value[0] in triggers) {
				queue.push([triggers[value[0]], value[1]]);
			}
		}
	}
}
init();
