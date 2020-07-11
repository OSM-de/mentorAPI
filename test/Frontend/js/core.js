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
	
	async function sendToAPI(action, headers=undefined, body="", jsonRequest=false, jsonResponse=false, callback=function(response) {console.log(response)}) {
			if (headers == undefined) {
				headers = {"Content-Type": "application/x-www-form-urlencoded"};
			}
			if (jsonRequest) {
				headers["Content-Type"] = "application/json";
			}
			
			let result;
			let response = await fetch(url + action, {"method": "POST", "credentials": "include", "headers": headers, "body": body});
			
			if (jsonResponse) {
				result = await response.json();
			} else {
				result = await response.text();
			}
			callback(result);
	}
	dir.sendToAPI = sendToAPI;
	
	function contactmethods(callback=function(resp) {console.log(response)}) {
		sendToAPI("contactmethods", callback);
	}
	dir.contactmethods = contactmethods;
	
	function searchAround(jsonObject, To) {
		
		if (jsonObject.location == undefined) { //the search radius limit is missing
			return To(msg["'location' required"]);
		}
		if (jsonObject.id != undefined) { //illegal property
			return To(msg["'id' not allowed"]);
		}
		
		sendToAPI("searchpeople", body=jsonObject, jsonRequest=true, jsonResponse=true, callback=callback);
	}
	dir.searchAround = searchAround;
	
	function changeProfile(jsonObject, To) {
		
		function callb(resp) {
			return To(msg[resp]);
		}
		
		sendToAPI("changeprofile", body=jsonObject, jsonRequest=true, callback=callb);
	}
	dir.changeProfile = changeProfile;
	
	function removeProfile(To, api="removeprofile") {
		
		function callb(resp) {
			return To(msg[resp]);
		}
		
		sendToAPI(api, callback=callb);
	}
	dir.removeProfile = removeProfile;
	
	function createProfile(To) {
		return removeProfile(To, api="createprofile");
	}
	dir.createProfile = createProfile;
	
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
		
		sendToAPI("showprofile", jsonResponse=true, callback=callb);
	}
	dir.myuser = myuser;
	
	return dir;
}
