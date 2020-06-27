# Community controlled regions

**Community conrolled regions for community building and for the community to provide newbies a way to find a mentor who helps in mastering OpenStreetMap**

Here are the files needed for the `region` module in [lib](../lib) to make sense. It allows the user of _mentorAPI_ (usage recognized or not) to filter search results by region (and therefore other users) and to set the region in case the particular user wants to create a profile. The module is responsive of region unification (Only one version of `hamburg` and `hh` should be in the database so the module must resolve the user input `hamburg` to `hh` or as the community decided. At the same time the module must also resolve a search of `hamburg` to `hh` or as the community decided). It uses the JSON files in this directory for doing so and for all other region related things.

## Motive

- GDPR compliance by abstracting and generalizing the home - preferably but it depends on how _mentorAPI_ will be used - location
- filtering out noice: Many users would apply offset to their location e.g. point the marker to a location of a supermarket (near) their home location. This leads to unorthogonality where some unveil their exact home location and where some doing the offset thing. This makes the filter algorithm less good, decreasing its result quality.
  With the layering/abstracting I hope that many feel good with unveiling in which region they (live)
- developing a new format for working with human readable region/bounding box logic rather than with machine logic as exposed with location services using decimal representations of a particular point on the earth.
- abstent on using the postgis extension for PostgreSQL.
- providing an easy way for communities to create an orthogonal way of finding people.
- reducing or preventing data which no one can handle properly coming into the database. A database generally advertises orthogonality and tidiness and therefore should follow its own advertisement.

## Good practise of using this mechanism

**Do only map region names.**

- **Don't use** this mechanism to indicate that you're living nearby a prominent living or dead person like `oonagh` by using e.g. `germany, stuttgard, oonagh` in your profile. Here `oonagh` is the name of a german female singer.  Such region mapping make use of the verb _nearby_ and is likely not defined as a quantitative definition like _around 1km_ (thought you could define and try to enforce it but please read furher). Therefore such region mapping would be unorthogonal because the verb _nearby_ is not defined equally and orthogonally (not the case if you quantitative define it like _around 1km_ but please read further). It is also not compliant to the motives of this mechanism because _nearby_ requires that you need to know the exact or nearly exact living position of a particular person you refer to yourself _being nearby to_. This has several problems: People have a right of private space. Doing such region mapping would deny them to have this. Also law might also deny it and morally it would be questionable because you should not _profit yourself_ without the person you benefit from knowing or supporting it.

- **I don't encourage but you can make use of** this mechanism to create "artificial region names" only your community knows. E.g. your community knows that `germany, hamburg, barmbek-nord` means `germany, cityfun, preparationcenter` but people outside the scope of your community don't know that.

- **Don't use** this mechanism to indicate that you're living nearby a memorial or another special object by using e.g. `france, paris, eiffel tower` in your profile. Such region mapping make use of the verb *nearby* and is likely not defined as a quantitative definition like *around 1km*. Therefore such region mapping would be unorthogonal because the verb *nearby* is not defined equally and orthogonally. And it would be questionable because you should not *profit yourself* from something special happening or being there. Thought you could comply with my motive by quantitative defining the verb _nearby_ by saying and enforcing that it means _around 1km_. But it would be still questionable (see my _not 'profit yourself' from_ statement).

- **Make use of** this mechanism to indicate that you're living inside a particular area either defined by government or another official authority or defined by the particular society living in there and accepted broadly by the others. But please be careful because society definitions are hard and most times not precise nor quantitative defined (society usually hates mathematics :)) Such conditions often occurr if such labelling of areas is traditional and therefore broadly accepted and understood. And the government or another official authority trying to modernize this. If both variants exist you should support both options and connect e.g. the official one to the unofficial one using a `__redirect` which is non-bidirectional e.g.
  
  **syntactical legal:**
  
  - e.g.: `<country>, <city>, <official suburb name>` redirecting to `<country>, <city>, <suburb name defined by local community>`
  - e.g.: `<country>, <city>, <suburb name defined by local community>` redirecting to `<country>, <city>, <official suburb name>`
  
  **syntactical illegal:**
  
  - e.g.: `<country>, <city>, <official suburb name>` redirecting to `<country>, <city>, <suburb name defined by local community>` and `<country>, <city>, <suburb name defined by local community>` redirecting to `<country>, <city>, <official suburb name>` (this would result in a loop making the app to run in an endless loop or returning an error)
