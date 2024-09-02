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