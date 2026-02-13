###############################################################################
# This makefile was written by Marcelo Belentani de Bianchi                   #
# to help maintain the catalog and show how to use the tool.                  #
#                                                                             #
# @ 2022                                                                      #
###############################################################################

FELT = catalogo_Andean_Felt_in_BR.dat
CAT  = catalogo_RAW.dat

#
# This is Linux default tools
#
GREP_TOOL=grep
LIBREOFFICE_TOOL=libreoffice7.2
AWK_TOOL=awk
SED_TOOL=sed
FILE_TOOL=file
PYTHON3_TOOL=python3
DATE_TOOL=date
SORT_TOOL=sort
OPEN_TOOL=xdg-open
CUT_TOOL=cut

#
# Detect MacOS
#
ifeq "$(shell uname -s)"  "Darwin"
	GREP_TOOL=ggrep
	LIBREOFFICE_TOOL=soffice
	AWK_TOOL=awk
	SED_TOOL=sed
	FILE_TOOL=file
	PYTHON3_TOOL=python3
	DATE_TOOL=gdate
	SORT_TOOL=gsort
	OPEN_TOOL=open
endif

#
# Targets
#
.PHONY: release

check: c_eol c_tab c_spaces c_nf c_dot_lat c_dot_lon c_cat c_locality
	@echo "Check Done."
	@echo ""
	@echo "  -- Use 'make help' for other options."

help:
	@echo "Makefile commands:"
	@echo ""
	@echo "  make check    Make a basic routine check of the files, uses this after editing any .dat file."
	@echo "  make fix      Tries to fix basic issues with the files."
	@echo "  make release  Prepare a new release set of files."
	@echo "  make map      Uses GMT6 to plot a basic map of the catalog (version SCR-2.5)"
	@echo "  make help     This help Message"
	@echo ""

c_nf:
	@echo "Checking that the number of fields up to category is 11"
	@echo ""
	@$(CUT_TOOL) -c1-55 $(CAT) | $(AWK_TOOL) 'NF!=11 {print " "$$0}'
	@echo ""
#
# Check that eol are consistent
#
c_eol:
	@echo "Check end of lines"
	@echo ""
	@$(FILE_TOOL) -e csv *.dat | $(AWK_TOOL) '{print " "$$0}'
	@echo ""

#
# Check that there are not tabs in file
#
c_tab:
	@echo "Checking tabs"
	@echo ""
	@$(GREP_TOOL) -Pc '\t+' $$(ls -1 *.csv *.dat 2>/dev/null) | $(AWK_TOOL) -F":" '{print " "$$2" entries found in "$$1}'
	@echo ""

#
# Check that there are no spaces at end of lines
#
c_spaces:
	@echo "Checking spaces"
	@echo ""
	@$(GREP_TOOL) -Pc '\s+$$' *.dat | $(AWK_TOOL) -F":" '{print " "$$2" entries found in "$$1}'
	@echo ""

#
# Check latitude dot position
#
c_dot_lat:
	@echo "Checking . on latitude"
	@echo ""
	@cut -c 23 $(CAT) | paste - $(CAT) | grep -v '^[.-]' | awk '{print "\t",$$0}'
	@echo ""
	@echo ""

#
# Check longitude dot position
#
c_dot_lon:
	@echo "Checking . on longitude"
	@echo ""
	@cut -c 30 $(CAT) | paste - $(CAT) | grep -v '^[.-]' | awk '{print "\t",$$0}'
	@echo ""
	@echo ""

#
# Check categories
#
c_cat:
	@echo "Checking category"
	@echo ""
	@cut -c 55 $(CAT)  | paste - $(CAT) | grep -v '^[ABCDEIR]' | awk '{print "\t",$$0}'
	@echo ""
	@echo ""

#
# Check locality field separation
#
c_locality:
	@echo "Checking locality field ... "
	@echo ""
	@echo "... do not start with letters:"
	@cut -c 67 $(CAT)  | paste - $(CAT)  | grep -v "^[A-Za-z]" | awk '{print "\t",$$0}'
	@echo ""
	@echo "... merged with previous field (start):"
	@cut -c 66 $(CAT)  | paste - $(CAT)  | grep -v "^[ ]" | awk '{print "\t",$$0}'
	@echo ""
	@echo "... merged with previous field (end):"
	@cat $(CAT) | colrm 1 88 | colrm 2 | paste - $(CAT)  | grep -v '^[ ]'
	@echo ""


#
# Basic fix of .dat files
#
fix:
	@echo "cleaning EOL"
	@for f in *.dat; do flip -vub $$f; done
	@echo ""
	
	@echo "Cleaning spaces in dat files"
	@for f in *.dat ; do echo " > Removing spaces in $$f"; $(SED_TOOL) -E 's/\s+$$//g' $$f > _TMP; mv _TMP $$f; done
	@echo ""

#
# Map (depends on GMT 6.2+)
#
PS = map.ps
map:
	# Basemap
	@gmt psbasemap -R-75/-32/-35/7 -B1a5/1a5:."Sismos no Brasil (1720-2023, mag @~\263@~ 2,5)":WsNe -JM12 -Xc -Yc -K --FONT_TITLE="16p,Helvetica,black" > $(PS)
	@gmt makecpt -Cgeo -T-5000/5000/50 > _CPT
	@gmt grdview @earth_relief_04m -R -J -C_CPT -I+ -Qi -O -K >>$(PS)
	@gmt pscoast -R -J -W0.5p,black -A10000 -N1 -I0.5 -O -K >>$(PS)
	
	# Felt Events
	@$(PYTHON3_TOOL) converter.py -m raw -of gmt $(FELT) |\
	   $(SORT_TOOL) -k+3 -n -r |\
	   gmt psxy -R -J -O -K -Sc -W1.2p,80 -t15 >> $(PS)
	
	# Historic Events
	@$(PYTHON3_TOOL) converter.py -m scr2.5 -of gmt $(CAT) -H |\
	   $(SORT_TOOL) -k+3 -n -r |\
	   gmt psxy -R -J -O -K -Sc -W0.5p,80 -Gblue -t15 >> $(PS)
	
	# Instrumental Events
	@$(PYTHON3_TOOL) converter.py -m scr2.5 -of gmt $(CAT) -I |\
	   $(SORT_TOOL) -k+3 -n -r |\
	   gmt psxy -R -J -O -K -Sc -W0.5p,white -Gred -t45 >> $(PS)
	
	# Color scale & Legend
	@gmt psscale -R -J -DJRM -O -K -C_CPT -Bf500a1000:"Topografia (m)": --FONT_LABEL="12p,Helvetica,black" >> $(PS)
	@$(PYTHON3_TOOL) converter.py --gmt-legend |\
	   gmt pslegend -R -J -O -K -DJCB+w12/2.3+o0.0/0.25 >> $(PS)

	# Timestamp
	@echo "Atualizado em: $$($(DATE_TOOL) +%Y-%m-%d -u)" | gmt pstext -R -J -K -O -F+f09p,Helvetica-Oblique,black+cBR+jBR -Dj0.1/0.1 -Gwhite@20 >> $(PS)

	# Finalizing
	@gmt psxy -R -J -O -T >> $(PS)
	@gmt psconvert -A+m0.5c/0.5c -P -Tf $(PS)
	@rm -f _CPT gmt.history gmt.conf $(PS)

	# File is $(subst .ps,.pdf,$(PS))
	@$(OPEN_TOOL) $(subst .ps,.pdf,$(PS)) 2> /dev/null

#
# Making a new release:
#
rcode = "v2022Jan27"
release:
	@echo "Making release $(rcode) into release folder"
	@echo ""
	
	@mkdir -v release
	@echo ""
	
	@echo "Copying $$(cp -iv $(FELT) release/catalogo_Andean_Felt_in_BR_$(rcode).dat)"
	@echo ""
	
	@$(PYTHON3_TOOL) converter.py -v -of raw -m raw $(CAT) > release/catalogo_ate2020_RAW_$(rcode).dat
	@$(PYTHON3_TOOL) converter.py -v -of csv -m raw $(CAT) > release/catalogo_ate2020_RAW_$(rcode).csv
	@echo ""
	
	@$(PYTHON3_TOOL) converter.py -v -of raw -m clean $(CAT) > release/catalogo_ate2020_CLEAN_$(rcode).dat
	@$(PYTHON3_TOOL) converter.py -v -of csv -m clean $(CAT) > release/catalogo_ate2020_CLEAN_$(rcode).csv
	@echo ""
	
	@$(PYTHON3_TOOL) converter.py -v -of raw -m scr $(CAT) > release/catalogo_ate2020_SCR_$(rcode).dat
	@$(PYTHON3_TOOL) converter.py -v -of csv -m scr $(CAT) > release/catalogo_ate2020_SCR_$(rcode).csv
	@echo ""
	
	@$(PYTHON3_TOOL) converter.py -v -of raw -m scr2.5 $(CAT) > release/catalogo_ate2020_SCR_mag2.5_$(rcode).dat
	@$(PYTHON3_TOOL) converter.py -v -of csv -m scr2.5 $(CAT) > release/catalogo_ate2020_SCR_mag2.5_$(rcode).csv
	@echo ""
	
	@$(LIBREOFFICE_TOOL) --infilter='CSV:44,34,0,1' --convert-to xlsx --outdir release release/catalogo_ate2020_RAW_$(rcode).csv --headless
	@$(LIBREOFFICE_TOOL) --infilter='CSV:44,34,0,1' --convert-to xlsx --outdir release release/catalogo_ate2020_CLEAN_$(rcode).csv --headless
	@$(LIBREOFFICE_TOOL) --infilter='CSV:44,34,0,1' --convert-to xlsx --outdir release release/catalogo_ate2020_SCR_$(rcode).csv --headless
	@$(LIBREOFFICE_TOOL) --infilter='CSV:44,34,0,1' --convert-to xlsx --outdir release release/catalogo_ate2020_SCR_mag2.5_$(rcode).csv --headless
	
	@echo "Changing EOL to MS-DOS"
	@for f in release/*.dat; do flip -vmb $$f | $(AWK_TOOL) '{print " "$$0}'; done
	@echo ""
	@for f in release/*.csv; do flip -vmb $$f | $(AWK_TOOL) '{print " "$$0}'; done
	@echo ""
	
	@echo "Check EOL in MS-DOS mode (CRLF)"
	@$(FILE_TOOL) -e csv release/*.dat release/*.csv | $(AWK_TOOL) '{print " "$$0}'
	@echo ""
	
	@echo "Making a zip distribution release file:"
	@mv -iv release sisbra_$(rcode) | $(AWK_TOOL) '{print " "$$0}'
	@echo ""
	
	@echo "Generating checksums"
	@md5sum sisbra_$(rcode)/* | tee sisbra_$(rcode)/md5sum.lst | $(AWK_TOOL) '{print " "$$0}'
	@echo ""
	
	@echo "Making a distribution ZIP file"
	@zip -r sisbra_$(rcode).zip sisbra_$(rcode)
