export type EnumTextChoice = {label: string, value: string}

export type EnumTextChoices = Record<string, EnumTextChoice>

export const EnumAccountTypes: EnumTextChoices =  {
  'staff': {
    label: "Staff",
    value: "staff"
  },
  'user': {
    label: "User",
    value: "user"
  }
}

export const EnumContentTags: EnumTextChoices =  {
  'automated': {
    label: "Automated",
    value: "automated"
  },
  'user_giving_tips_with_content': {
    label: "User Giving Tips, post also contains original content",
    value: "user_giving_tips_with_content"
  },
  'user_giving_tips_without_content': {
    label: "User Giving Tips, no original content",
    value: "user_giving_tips_without_content"
  },
  'bot_tip_reply': {
    label: "Bot Tip Reply, automated reply to a tipping message, usually saying remaining balance",
    value: "bot_tip_reply"
  },
  'original_content': {
    label: "Original Content, a real human message, it is on-topic and valid user content (as opposed to spam, nonsense, or tipping-without-content), its not just "haha" or "great point"",
    value: "original_content"
  },
  'spam': {
    label: "Spam",
    value: "spam"
  },
  'off_topic': {
    label: "Off Topic - completely unrelated to channel topic, very low likelihood of being relevant discussion. If unsure, dont tag as off-topic.",
    value: "off_topic"
  },
  'hate_speech': {
    label: "Hate Speech - explicit racism, sexism, homophobia, transphobia, etc",
    value: "hate_speech"
  },
  'sexually_explicit': {
    label: "Sexually Explicit",
    value: "sexually_explicit"
  }
}