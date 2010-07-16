#!/bin/sh
PRODUCTNAME='gomobile.mobile'
I18NDOMAIN=$PRODUCTNAME

#i18ndude rebuild-pot --pot ./${PRODUCTNAME}.pot --merge ./i18n/generated.pot --exclude=`find ./profiles -name "*.*py"` --create ${I18NDOMAIN} .

rm ./locales/rebuild_i18n.log

i18ndude=$INS/bin/i18ndude

[[ ! -f $i18ndude ]] && i18ndude=i18ndude
echo using $i18ndude

# List of languages
LANGUAGES="en es fi"

# Create locales folder structure for languages
install -d locales
for lang in $LANGUAGES; do
    install -d ./locales/$lang/LC_MESSAGES
    touch ./locales/$lang/LC_MESSAGES/${PRODUCTNAME}.po
    touch ./i18n/${PRODUCTNAME}-plone-$lang.po
done

# Synchronise the .pot with the templates.
$i18ndude rebuild-pot --pot ./locales/${PRODUCTNAME}.pot  --create ${I18NDOMAIN} ./
$i18ndude rebuild-pot --pot ./i18n/${PRODUCTNAME}-plone.pot --create plone ./browser/portlets || exit 1

# Synchronise the resulting .pot with the .po files
$i18ndude sync --pot ./locales/${PRODUCTNAME}.pot ./locales/*/LC_MESSAGES/${PRODUCTNAME}.po
$i18ndude sync --pot ./i18n/${PRODUCTNAME}-plone.pot ./i18n/${PRODUCTNAME}-plone-*.po

WARNINGS=`find ./ -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-WARN' | wc -l`
ERRORS=`find ./ -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-ERROR' | wc -l`
FATAL=`find ./ -name "*pt"  | xargs i18ndude find-untranslated | grep -e '^-FATAL' | wc -l`

echo
echo "There are $WARNINGS warnings (possibly missing i18n markup)"
echo "There are $ERRORS errors (almost definitely missing i18n markup)"
echo "There are $FATAL fatal errors (template could not be parsed, eg. if it\'s not html)"
echo "For more details, run \'find . -name \"\*pt\" \| xargs i18ndude find-untranslated\' or" 
echo "Look the rebuild i18n log generate for this script called \'rebuild_i18n.log\' on locales dir" 

touch ./locales/rebuild_i18n.log

find ./ -name "*pt" | xargs $i18ndude find-untranslated > ./locales/rebuild_i18n.log
