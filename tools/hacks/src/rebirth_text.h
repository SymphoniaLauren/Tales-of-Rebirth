#ifndef __REBIRTH_TEXT_TYPES_H__
#define __REBIRTH_TEXT_TYPES_H__

#define _STR(a) #a

#define NL "\x01"
#define CR "\x02"

#define EM_DASH "\x9A\xF3"

#define TAG_BASE(t, b0, b1, b2, b3) _STR(\x##t) _STR(\x##b0) _STR(\x##b1) _STR(\x##b2) _STR(\x##b3)

#define VAR(b0, b1, b2, b3) TAG_BASE(04, b0, b1, b2, b3)
#define COLOR(b0, b1, b2, b3) TAG_BASE(05, b0, b1, b2, b3)
#define SCALE(b0, b1, b2, b3) TAG_BASE(06, b0, b1, b2, b3)
#define SPEED(b0, b1, b2, b3) TAG_BASE(07, b0, b1, b2, b3)
#define ITALIC(b0, b1, b2, b3) TAG_BASE(08, b0, b1, b2, b3)
#define NMB(b0, b1, b2, b3) TAG_BASE(09, b0, b1, b2, b3)
#define PTR(b0, b1, b2, b3) TAG_BASE(0A, b0, b1, b2, b3)
// #define NAME(b0, b1, b2, b3) TAG_BASE(0B, b0, b1, b2, b3)
#define ITEM(b0, b1, b2, b3) TAG_BASE(0C, b0, b1, b2, b3)
#define ICON(b0, b1, b2, b3) TAG_BASE(0D, b0, b1, b2, b3)
#define FONT(b0, b1, b2, b3) TAG_BASE(0E, b0, b1, b2, b3)
#define VOICE(b0, b1, b2, b3) TAG_BASE(0F, b0, b1, b2, b3)

#define BLUE "\x05\x01\x00\x00\x00"
#define RED "\x05\x02\x00\x00\x00"
#define PURPLE "\x05\x03\x00\x00\x00"
#define GREEN "\x05\x04\x00\x00\x00"
#define CYAN "\x05\x05\x00\x00\x00"
#define YELLOW "\x05\x06\x00\x00\x00"
#define WHITE "\x05\x07\x00\x00\x00"
#define GREY "\x05\x08\x00\x00\x00"
#define BLACK "\x05\x09\x00\x00\x00"

#define VEIGUE "\x0B\x01\x00\x00\x00"
#define MAO "\x0B\x02\x00\x00\x00"
#define EUGENE "\x0B\x03\x00\x00\x00"
#define ANNIE "\x0B\x04\x00\x00\x00"
#define TYTREE "\x0B\x05\x00\x00\x00"
#define HILDA "\x0B\x06\x00\x00\x00"
#define CLAIRE "\x0B\x07\x00\x00\x00"
#define AGARTE "\x0B\x08\x00\x00\x00"
#define ANNIE_NPC "\x0B\x09\x00\x00\x00"
#define LEADER "\x0B\xFF\x1F\x00\x00"

#define NO_ITALIC "\x08\x00\x00\x00\x00"

#endif /* __REBIRTH_TEXT_TYPES_H__ */
