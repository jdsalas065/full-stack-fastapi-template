import { apiClient } from "../api-client"
import type {
  Body_login_login_access_token,
  Message,
  NewPassword,
  Token,
  UserPublic,
} from "../types"

export class LoginService {
  /**
   * Login Access Token
   * OAuth2 compatible token login, get an access token for future requests
   */
  public static async loginAccessToken(data: {
    formData: Body_login_login_access_token
  }): Promise<Token> {
    const formData = new URLSearchParams()
    formData.append("username", data.formData.username)
    formData.append("password", data.formData.password)
    if (data.formData.grant_type) {
      formData.append("grant_type", data.formData.grant_type)
    }
    if (data.formData.scope) {
      formData.append("scope", data.formData.scope)
    }
    if (data.formData.client_id) {
      formData.append("client_id", data.formData.client_id)
    }
    if (data.formData.client_secret) {
      formData.append("client_secret", data.formData.client_secret)
    }

    const response = await apiClient.post<Token>(
      "/api/v1/login/access-token",
      formData,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      },
    )
    return response.data
  }

  /**
   * Test Token
   * Test access token
   */
  public static async testToken(): Promise<UserPublic> {
    const response = await apiClient.post<UserPublic>(
      "/api/v1/login/test-token",
    )
    return response.data
  }

  /**
   * Recover Password
   * Password Recovery
   */
  public static async recoverPassword(data: {
    email: string
  }): Promise<Message> {
    const response = await apiClient.post<Message>(
      `/api/v1/password-recovery/${encodeURIComponent(data.email)}`,
    )
    return response.data
  }

  /**
   * Reset Password
   * Reset password
   */
  public static async resetPassword(data: {
    requestBody: NewPassword
  }): Promise<Message> {
    const response = await apiClient.post<Message>(
      "/api/v1/reset-password/",
      data.requestBody,
    )
    return response.data
  }

  /**
   * Recover Password Html Content
   * HTML Content for Password Recovery
   */
  public static async recoverPasswordHtmlContent(data: {
    email: string
  }): Promise<string> {
    const response = await apiClient.post<string>(
      "/api/v1/password-recovery-html-content/" +
        encodeURIComponent(data.email),
    )
    return response.data
  }
}
