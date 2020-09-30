db.getCollection("band").aggregate(

	// Pipeline
	[
		// Stage 1
		{
			$match: {
			'genres': {$in: ['blues', 'electronic']},
			'catalogue_name' : { "$regex": "^O"},
			'hometown.county' : {$in: ['Clare', 'Cork', 'Kerry', 'Limerick', 'Tipperary', 'Waterford']}
			}
		},

		// Stage 2
		{
			$facet: {
			    "numbers_by_letter": [ { $group: {
			    // enter query here
			    _id: {$substr: ["$catalogue_name",0,1]},
			    bands: {$sum: 1}
			}}
			     ],
			    "bands_by_letter": [
			        { $match: {
			                // enter query here
			                "catalogue_name": { $regex: /^M/},
			            }
			        } 
			        
			 ],
			    // add more facets
			}
		},

	]

	// Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

);
