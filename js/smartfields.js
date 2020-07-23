function smartTypingField() {
	let dir = new Object();
	let n = 0;
	
	function createSmartSearch(element, searchtextlabel="Search", searchresultlabel="Search result", partslabel="options added to the search") {
		let address = "smartFields_ss" + String(n);
		n += 1;
		
		let out = `
		<div class='search' role='search' aria-label="${searchtextlabel}">
			<ul class='parts' id='${address}_parts' aria-label='${partslabel}'>
					
			</ul>
			<div class='searchandsuggestion'>
				<input type='text' role='searchbox' onkeydown='smartTypingFields_pressedOnSearchbox(event, "${address}")' placeholder='${searchtextlabel}' id='${address}_searchbox'/>
				<ul class='searchresult' aria-label='${searchresultlabel}' id='${address}_searchresult'>
				
			</ul>
			</div>
		</div>`
		
		let newSS = document.createElement("div");
		newSS.setAttribute("class", "smartFields");
		newSS.setAttribute("id", address);
		newSS.innerHTML = out;
		
		element.appendChild(newSS);
		return address;
		
		
	}
	dir.createSearch = createSmartSearch;
	
	return dir;
}
function smartTypingFields_pressedOnSearchbox(e, mother) {
	let code = e.key || event.code;
	let elem = e.target;
	let value = elem.value.replace(",", "");
	let parts = document.getElementById(mother + "_parts");
	
	if (code == "Enter" || code == "," || code == "Comma") {
		e.preventDefault();
		elem.value = "";
		
		let newPart = document.createElement("li");
		newPart.setAttribute("role", "checkbox");
		newPart.setAttribute("aria-checked", true);
		newPart.setAttribute("tabindex", 0);
		newPart.setAttribute("class", "option");
		newPart.innerHTML =`${value}<span aria-hidden='true' class='remove' onclick='event.target.parentNode.parentElement.removeChild(event.target.parentElement)'>x</span>`;
		newPart.addEventListener("click", function() { event.target.parentNode.removeChild(event.target) });
		parts.appendChild(newPart);
	}
}
