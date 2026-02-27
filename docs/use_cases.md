# Use Cases

## UC-1: Search by author and branch
**Prompt:** "Which books by Väinö Linna are available in Munkkiniemi?"
**Expected behaviour:**
1. Resolve "Munkkiniemi" → Finna building code
2. Search Finna: `lookfor=väinö linna`, `type=Author`, `filter[]=building:{code}`, `filter[]=format:"0/Book/"`
3. Return list of matching titles with year and Finna link
**Status:** not yet implemented

## UC-2: Search by title
**Prompt:** "Does the library have Tuntematon sotilas?"
**Expected behaviour:**
1. Search Finna: `lookfor=tuntematon sotilas`, `type=Title`, `filter[]=building:"0/Helmet/"`
2. Return matching records with branch locations
**Status:** not yet implemented

## UC-3: Opening hours
**Prompt:** "When is Kallio library open tomorrow?"
**Expected behaviour:**
1. Resolve "Kallio" → Kirkanta library ID (84860)
2. Fetch schedules for that library
3. Return tomorrow's opening hours
**Status:** not yet implemented

## UC-4: General free-text search
**Prompt:** "I'm looking for children's books about dinosaurs in Espoo"
**Expected behaviour:**
1. Search Finna: `lookfor=dinosaurus lapset` (or similar), `filter[]=building:"1/Helmet/e/"`, `filter[]=format:"0/Book/"`
2. Return results with branch info
**Status:** not yet implemented

## UC-5: Ambiguous branch name
**Prompt:** "What's available in Haaga?"
**Expected behaviour:**
1. Fuzzy match "Haaga" → multiple hits (Etelä-Haaga, Pohjois-Haaga)
2. Agent asks user to clarify which branch
**Status:** not yet implemented

## UC-6: Multi-format search
**Prompt:** "Are there audiobooks of Sinuhe egyptiläinen?"
**Expected behaviour:**
1. Search Finna: `lookfor=sinuhe egyptiläinen`, `filter[]=format:"1/Sound/"`, `filter[]=building:"0/Helmet/"`
2. Return matching audio records
**Status:** not yet implemented
