function mentorAPI(url) {
	let dir = new Object();
	let msg = {
			"not logged in": {"error": "LOGINREQUIRED"},
			"'location' required": {"error": "LOCATIONREQUIRED"},
			"'id' not allowed": {"error": "IDILLEGAL"},
			"{}": {"info": "NOPROFILE"},
			"OK": {"info": "SUCCESS"},
			"profile not existing": {"error": "NOPROFILE"}
	}
	
	if (url == undefined) { //FOR DEVELOPMENT PURPOSE ONLY
		url = "http://localhost:9090/";
	}
	if (!url.endsWith("/")) {
		url += "/";
	}
	
	async function sendToAPI(action, callback, args) {
		if (args.headers == undefined || Object.keys(args["headers"]).length == 0) {
			args.headers = {"Content-Type": "text/plain"} //{"Content-Type": "application/x-www-form-urlencoded"};
		}
		if (args.jsonRequest) {
			args.headers["Content-Type"] = "application/json";
		}
		
		let result;
		let response = await fetch(url + action, {"method": "POST", "credentials": "include", "cache": "force-cache", "headers": args.headers, "body": JSON.stringify(args.body)});
		if (args.jsonResponse) {
			result = await response.json();
		} else {
			result = await response.text();
		}
		callback(result);
	}
	dir.sendToAPI = sendToAPI;
	
	function contactmethods(To) {
		sendToAPI("contactmethods", To, {});
	}
	dir.contactmethods = contactmethods;
	
	function searchAround(jsonObject, To) {
		
		if (jsonObject.location == undefined) { //the search radius limit is missing
			return To(msg["'location' required"]);
		}
		if (jsonObject.id != undefined) { //illegal property
			return To(msg["'id' not allowed"]);
		}
		
		sendToAPI("searchpeople", To, {body: jsonObject, jsonRequest: true, jsonResponse: true});
	}
	dir.searchAround = searchAround;
	
	function changeProfile(jsonObject, To) {
		
		function callb(resp) {
			return To(msg[resp]);
		}
		
		sendToAPI("changeprofile", callb, {body: jsonObject, jsonRequest: true});
	}
	dir.changeProfile = changeProfile;
	
	function removeProfile(To, api="removeprofile") {
		
		function callb(resp) {
			return To(msg[resp]);
		}
		
		sendToAPI(api, callb, {});
	}
	dir.removeProfile = removeProfile;
	
	function createProfile(To) {
		removeProfile(To, api="createprofile");
	}
	dir.createProfile = createProfile;
	
	function searchForRegion(params, To) {
		return sendToAPI("autocompleteRegion", To, {body: params, jsonRequest: true, jsonResponse: true});
	}
	dir.searchForRegion = searchForRegion;
	
	function myuser(To) {
		function callb(resp) {
			if (Object.keys(resp).length == 0) { //check emptyness
				return To(msg["{}"]);
			}
			if (resp.error != undefined) { //an error occurred
				return To(msg[resp.error]);
			}
			for (x in resp) {
				return To(resp[x]);
			}
		}
		
		sendToAPI("showprofile", callb, {jsonResponse: true});
	}
	dir.myuser = myuser;
	
	function loginWith(provider) {
		function callb(resp) {
			console.info("mentorAPI:\nRedirecting to '" + provider + "'s OAuth login page...");
			location.href = resp;
		}
		if (provider == undefined || provider == "") {
			console.error("mentorAPI:\nfunction 'loginWith' called without providing a provider code. Call it like e.g.: `loginWith(\"osm\") in order to log in with an OpenStreetMap account.");
			return false;
		}
		sendToAPI("login/" + provider, callb, {});
	}
	dir.loginWith = loginWith;
	
	return dir;
}
