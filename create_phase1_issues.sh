#!/bin/bash

gh issue create --title "Setup backend project structure" --body "Create backend folders: backend, engine, api, models, utils" --label "phase:1,backend,setup"

gh issue create --title "Initialize backend server" --body "Set up Flask or FastAPI server" --label "phase:1,backend"

gh issue create --title "Create base API route" --body "GET /api/test returns API is running" --label "phase:1,api"

gh issue create --title "Create Character data model" --body "Define character structure" --label "phase:1,models"

gh issue create --title "Create Stats data model" --body "Define stats structure" --label "phase:1,models"

gh issue create --title "Create Defenses data model" --body "Define defenses structure" --label "phase:1,models"

gh issue create --title "Create Item data model" --body "Define item structure" --label "phase:1,models"

gh issue create --title "Create Affix data model" --body "Define affix structure" --label "phase:1,models"

gh issue create --title "Create Skill data model" --body "Define skill structure" --label "phase:1,models"

gh issue create --title "Create sample character JSON" --body "Create test payload" --label "phase:1,testing"

gh issue create --title "Create /simulate endpoint" --body "Stub endpoint" --label "phase:1,api"

gh issue create --title "Add input validation" --body "Validate request data" --label "phase:1,api"

gh issue create --title "Parse API into models" --body "Convert JSON to objects" --label "phase:1,backend"

gh issue create --title "Add logging" --body "Log requests and errors" --label "phase:1,backend"

gh issue create --title "Test full API flow" --body "End-to-end test" --label "phase:1,testing"
